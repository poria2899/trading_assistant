from datetime import date, time
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from .models import Direction, Result, Timeframe, Trade


class TradeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="trader1", password="SuperSecret123!")

    def _make_trade(self, **overrides):
        defaults = dict(
            user=self.user,
            date=date(2026, 9, 1),
            time=time(14, 30),
            asset="XAUUSD",
            direction=Direction.BUY,
            timeframe=Timeframe.H1,
            position_size=Decimal("1.5"),
            entry_price=Decimal("2450.500"),
            result=Result.WIN,
        )
        defaults.update(overrides)
        return Trade.objects.create(**defaults)

    def test_valid_trade_can_be_created(self):
        trade = self._make_trade()
        self.assertEqual(Trade.objects.count(), 1)
        self.assertEqual(trade.asset, "XAUUSD")

    def test_trade_belongs_to_correct_user(self):
        other_user = User.objects.create_user(username="trader2", password="SuperSecret123!")
        trade = self._make_trade()
        other_trade = self._make_trade(user=other_user, asset="EURUSD")

        self.assertEqual(trade.user, self.user)
        self.assertEqual(other_trade.user, other_user)
        self.assertEqual(Trade.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Trade.objects.filter(user=other_user).count(), 1)

    def test_user_is_required(self):
        with self.assertRaises(IntegrityError):
            Trade.objects.create(
                date=date(2026, 9, 1),
                time=time(14, 30),
                asset="XAUUSD",
                direction=Direction.BUY,
                timeframe=Timeframe.H1,
                position_size=Decimal("1.0"),
                entry_price=Decimal("2450.5"),
                result=Result.OPEN,
            )

    def test_optional_fields_can_be_blank(self):
        trade = self._make_trade(
            stop_loss=None,
            take_profit=None,
            exit_price=None,
            risk_amount=None,
            strategy="",
            session="",
            notes="",
            tags="",
        )
        self.assertIsNone(trade.stop_loss)
        self.assertEqual(trade.strategy, "")

    def test_direction_choices(self):
        buy = self._make_trade(direction=Direction.BUY)
        sell = self._make_trade(direction=Direction.SELL, asset="EURUSD")
        self.assertEqual(buy.direction, "BUY")
        self.assertEqual(sell.direction, "SELL")
        self.assertEqual(sell.get_direction_display(), "Sell")

    def test_timeframe_choices(self):
        for tf in ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]:
            trade = self._make_trade(timeframe=tf, asset="EURUSD")
            self.assertEqual(trade.timeframe, tf)

    def test_result_choices(self):
        for result in [Result.OPEN, Result.WIN, Result.LOSS, Result.BREAKEVEN]:
            trade = self._make_trade(result=result, asset="EURUSD")
            self.assertEqual(trade.result, result)

    def test_result_defaults_to_open_when_not_specified(self):
        trade = Trade.objects.create(
            user=self.user,
            date=date(2026, 9, 1),
            time=time(9, 0),
            asset="BTCUSDT",
            direction=Direction.BUY,
            timeframe=Timeframe.M15,
            position_size=Decimal("0.10"),
            entry_price=Decimal("60000.00000"),
        )
        self.assertEqual(trade.result, Result.OPEN)

    def test_str_representation(self):
        trade = self._make_trade()
        text = str(trade)
        self.assertIn("XAUUSD", text)
        self.assertIn("BUY", text)
        self.assertIn("2026-09-01", text)

    def test_default_ordering_is_most_recent_first(self):
        older = self._make_trade(date=date(2026, 8, 1), asset="EURUSD")
        newer = self._make_trade(date=date(2026, 9, 1), asset="GBPUSD")
        trades = list(Trade.objects.all())
        self.assertEqual(trades[0], newer)
        self.assertEqual(trades[1], older)
