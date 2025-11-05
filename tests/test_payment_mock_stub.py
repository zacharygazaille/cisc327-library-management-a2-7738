import pytest
from unittest.mock import Mock, ANY
from services.library_service import pay_late_fees
from services.library_service import refund_late_fee_payment
from services.payment_service import PaymentGateway

def test_pay_late_fees_success(mocker):
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 1, 'title': 'Book A'})
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'days_overdue': 3, 'fee_amount': 4.50})
    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.return_value = (True, "txn_123456", "Processed")
    success, message, txn = pay_late_fees("123456", 1, payment_gateway=gateway)
    assert success is True
    assert txn == "txn_123456"
    assert "successful" in message
    gateway.process_payment.assert_called_once_with(patron_id="123456", amount=4.50, description=ANY)

def test_pay_late_fees_payment_declined(mocker):
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 2, 'title': 'Book B'})
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'days_overdue': 2, 'fee_amount': 2.00})
    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.return_value = (False, None, "Card declined")
    success, message, txn = pay_late_fees("123456", 2, payment_gateway=gateway)
    assert success is False
    assert txn == None
    assert "failed" in message
    gateway.process_payment.assert_called_once_with(patron_id="123456", amount=2.00, description=ANY)

def test_pay_late_fees_invalid_patron_id(mocker):
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 3, 'title': 'Book C'})
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'days_overdue': 1, 'fee_amount': 1.00})
    gateway = Mock(spec=PaymentGateway)
    success, message, txn = pay_late_fees("abc", 3, payment_gateway=gateway)
    assert success is False
    assert txn == None
    assert "Invalid patron ID" in message
    gateway.process_payment.assert_not_called()

def test_pay_late_fees_zero_late_fees(mocker):
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 4, 'title': 'Book D'})
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'days_overdue': 0, 'fee_amount': 0.00})
    gateway = Mock(spec=PaymentGateway)
    success, message, txn = pay_late_fees("123456", 4, payment_gateway=gateway)
    assert success is False
    assert txn == None
    assert "No late fees" in message
    gateway.process_payment.assert_not_called()

def test_pay_late_fees_network_error(mocker):
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 5, 'title': 'Book E'})
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'days_overdue': 4, 'fee_amount': 6.75})
    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.side_effect = Exception("Network error")
    success, message, txn = pay_late_fees("123456", 5, payment_gateway=gateway)
    assert success is False
    assert txn == None
    assert "processing error" in message
    gateway.process_payment.assert_called_once()

def test_pay_late_fees_no_fee_amount(mocker):
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 5, 'title': 'Book E'})
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'days_overdue': 4})
    gateway = Mock(spec=PaymentGateway)
    success, message, txn = pay_late_fees("123456", 5, payment_gateway=gateway)
    assert success is False
    assert txn == None
    assert "Unable to calculate" in message
    gateway.process_payment.assert_not_called()

def test_pay_late_fees_no_book(mocker):
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'days_overdue': 4, 'fee_amount': 6.75})
    gateway = Mock(spec=PaymentGateway)
    success, message, txn = pay_late_fees("123456", 5, payment_gateway=gateway)
    assert success is False
    assert txn == None
    assert "Book not found." in message
    gateway.process_payment.assert_not_called()

def test_pay_late_fees_no_pg(mocker):
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 5, 'title': 'Book E'})
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'days_overdue': 4, 'fee_amount': 6.75})
    success, message, txn = pay_late_fees("123456", 5)
    assert success is True # payment gateway will automatically be created and payment will succeed
    assert "successful" in message

def test_refund_late_fee_payment_success(mocker):
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (True, "rf_123456")
    success, message = refund_late_fee_payment("txn_123456", 5.00, payment_gateway=gateway)
    assert success is True
    assert "rf_123456" in message
    gateway.refund_payment.assert_called_once()

def test_refund_late_fee_payment_invalid_txn_id(mocker):
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (True, "rf_123456")
    success, message = refund_late_fee_payment("taxid_123456", 5.00, payment_gateway=gateway)
    assert success is False
    assert "Invalid transaction ID" in message
    gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_refund_amount_negative(mocker):
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (True, "rf_123456")
    success, message = refund_late_fee_payment("txn_123456", -5.00, payment_gateway=gateway)
    assert success is False
    assert "greater than 0" in message
    gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_refund_amount_zero(mocker):
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (True, "rf_123456")
    success, message = refund_late_fee_payment("txn_123456", 0.00, payment_gateway=gateway)
    assert success is False
    assert "greater than 0" in message
    gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_refund_amount_exceeds_15(mocker):
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (True, "rf_123456")
    success, message = refund_late_fee_payment("txn_123456", 16.00, payment_gateway=gateway)
    assert success is False
    assert "exceeds maximum late fee" in message
    gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_no_pg(mocker):
    success, message = refund_late_fee_payment("txn_123456", 1.00, payment_gateway=None)
    assert success is True # payment gateway will automatically be created and payment will succeed
    assert "txn_123456" in message

def test_refund_late_fee_payment_failed(mocker):
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (False, "Insufficient funds")
    success, message = refund_late_fee_payment("txn_123456", 1.00, payment_gateway=gateway)
    assert success is False
    assert "Refund failed" in message
    gateway.refund_payment.assert_called_once_with("txn_123456", 1.00)

def test_refund_late_fee_payment_error(mocker):
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.side_effect = Exception("Network error")
    success, message = refund_late_fee_payment("txn_123456", 1.00, payment_gateway=gateway)
    assert success is False
    assert "Refund processing error" in message
    gateway.refund_payment.assert_called_once_with("txn_123456", 1.00)