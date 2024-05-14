from rest_framework import serializers
from .models import Book, Member, Transaction

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'stock']

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'name', 'outstanding_debt']

class TransactionSerializer(serializers.ModelSerializer):
    member = MemberSerializer()
    book = BookSerializer()
    
    class Meta:
        model = Transaction
        fields = ['id', 'book', 'member', 'book_issued_date', 'book_returned_date', 'rent_fee']