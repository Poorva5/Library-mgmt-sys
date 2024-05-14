from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Book, Member, Transaction
from .serializers import BookSerializer, MemberSerializer, TransactionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime
from decimal import Decimal
import requests


class BookView(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    
    @action(detail=False, methods=['post'])
    def import_books(self, request):
        search = request.data.get('search', '')
        num_books = request.data.get('num_books', 32)
        
        books_imported = 0
        page = 1
        
        while books_imported < num_books:
            response = requests.get(f'https://gutendex.com/books/?search={search}&page={page}')
            if response.status_code != 200:
                return Response({"error": "Failed to fetch books"}, status=status.HTTP_400_BAD_REQUEST)
            
            data = response.json()
            books = data.get('results', [])
            
            if not books:
                break 
            
            for book_data in books:
                if books_imported >= num_books:
                    break
                
                book_title = book_data.get('title', '')
                book_author = ', '.join([author['name'] for author in book_data.get('authors', [])])

                # Create the book objects
                Book.objects.create(
                    title=book_title,
                    author=book_author,
                    stock=1 )
                books_imported += 1
            
            page += 1
        
        return Response({"message": f"Imported {books_imported} books successfully."}, status=status.HTTP_201_CREATED)

class MemberView(viewsets.ModelViewSet):
    serializer_class = MemberSerializer
    queryset = Member.objects.all()

class TransactionView(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    
    @action(detail=False, methods=['post'])
    def issue_book(self, request):
        book_id = request.data.get('book_id')
        member_id = request.data.get('member_id')
        
        try:
            book = Book.objects.get(pk=book_id)
            member = Member.objects.get(pk=member_id)
        except (Book.DoesNotExist, Member.DoesNotExist):
            return Response({"error": "Transaction does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        if book.stock <= 0:
            return Response({"error": "Book is Out of stock."}, status=status.HTTP_400_BAD_REQUEST)
        
        transaction = Transaction.objects.create(book=book, member=member)
        book.stock -= 1
        book.save()
        
        return Response({"message": "Book issued successfully."}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def return_book(self, request):
        transaction_id = request.data.get('transaction_id')
        rent_fee = request.data.get('rent_fee')

        try:
            transaction = Transaction.objects.get(pk=transaction_id)
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction does not exist."}, status=status.HTTP_404_NOT_FOUND)

        transaction.book_returned_date = datetime.now().date()
        transaction.rent_fee = Decimal(rent_fee) if rent_fee else Decimal('0.00')
        transaction.save()
        
        book = transaction.book
        book.stock += 1
        book.save()

        member = transaction.member
        
        if member.outstanding_debt is None:
            member.outstanding_debt = Decimal('0.00')
        
        member.outstanding_debt += transaction.rent_fee
        
        if member.outstanding_debt > Decimal('500.00'):
            return Response({"error": "Outstanding debt exceeds Rs. 500."}, status=status.HTTP_400_BAD_REQUEST)
        member.save()
        
        return Response({"message": "Book returned successfully."}, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['get'])
    def search_books(self, request):
        name = request.query_params.get('name')
        author = request.query_params.get('author')

        if not name and not author:
            return Response({"error": "Please Provide author name or book name"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Book.objects.all()

        if name:
            queryset = queryset.filter(title__icontains=name)
        if author:
            queryset = queryset.filter(author__icontains=author)

        serializer = BookSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
    