from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(default=0)
    
    def _str__(self):
        return self.title


class Member(models.Model):
    name = models.CharField(max_length=100)
    outstanding_debt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.name

class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book_issued_date = models.DateField(auto_now_add=True)
    book_returned_date = models.DateField(null=True, blank=True)
    rent_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    
    def __str__(self):
        return f"{self.book.title} - {self.member.name}"