import pytest
from unittest.mock import Mock
from services.library_service import refund_late_fee_payment
from services.payment_service import PaymentGateway

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