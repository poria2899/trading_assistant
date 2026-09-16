from datetime import date, time
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

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


class AddTradeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="trader1", password="SuperSecret123!")
        self.other_user = User.objects.create_user(username="trader2", password="SuperSecret123!")
        self.url = reverse("journal:add_trade")

    def _valid_payload(self, **overrides):
        payload = {
            "date": "2026-09-01",
            "time": "14:30",
            "asset": "XAUUSD",
            "direction": Direction.BUY,
            "timeframe": Timeframe.H1,
            "position_size": "1.50",
            "entry_price": "2450.50000",
            "stop_loss": "",
            "take_profit": "",
            "exit_price": "",
            "strategy": "",
            "session": "",
            "risk_amount": "",
            "result": Result.OPEN,
            "notes": "",
            "tags": "",
        }
        payload.update(overrides)
        return payload

    def test_anonymous_user_cannot_access_add_trade_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_authenticated_user_can_access_add_trade_page(self):
        self.client.login(username="trader1", password="SuperSecret123!")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add Trade")

    def test_valid_submission_creates_trade(self):
        self.client.login(username="trader1", password="SuperSecret123!")
        response = self.client.post(self.url, self._valid_payload())
        self.assertEqual(Trade.objects.count(), 1)
        trade = Trade.objects.get()
        self.assertEqual(trade.asset, "XAUUSD")
        self.assertEqual(response.status_code, 302)

    def test_created_trade_belongs_to_logged_in_user(self):
        self.client.login(username="trader1", password="SuperSecret123!")
        self.client.post(self.url, self._valid_payload())
        trade = Trade.objects.get()
        self.assertEqual(trade.user, self.user)

    def test_submitted_user_field_is_ignored(self):
        # The form has no `user` field at all, so even if a malicious
        # payload includes a `user` key, it cannot change the owner.
        self.client.login(username="trader1", password="SuperSecret123!")
        payload = self._valid_payload(user=self.other_user.pk)
        self.client.post(self.url, payload)
        trade = Trade.objects.get()
        self.assertEqual(trade.user, self.user)
        self.assertNotEqual(trade.user, self.other_user)

    def test_invalid_submission_missing_required_field_is_rejected(self):
        self.client.login(username="trader1", password="SuperSecret123!")
        payload = self._valid_payload(asset="")
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Trade.objects.count(), 0)
        self.assertContains(response, "This field is required")

    def test_successful_creation_redirects_to_journal_index(self):
        self.client.login(username="trader1", password="SuperSecret123!")
        response = self.client.post(self.url, self._valid_payload())
        self.assertRedirects(response, reverse("journal:index"))

    def test_success_message_is_displayed(self):
        self.client.login(username="trader1", password="SuperSecret123!")
        response = self.client.post(self.url, self._valid_payload(), follow=True)
        messages = list(response.context["messages"])
        self.assertTrue(any("Trade added successfully." in str(m) for m in messages))

    def test_optional_fields_can_be_omitted(self):
        self.client.login(username="trader1", password="SuperSecret123!")
        response = self.client.post(self.url, self._valid_payload())
        self.assertEqual(response.status_code, 302)
        trade = Trade.objects.get()
        self.assertIsNone(trade.stop_loss)
        self.assertEqual(trade.strategy, "")

    def test_anonymous_user_cannot_submit_trade(self):
        response = self.client.post(self.url, self._valid_payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Trade.objects.count(), 0)


class TradeDetailViewTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username="usera", password="SuperSecret123!")
        self.user_b = User.objects.create_user(username="userb", password="SuperSecret123!")

        self.trade_a = Trade.objects.create(
            user=self.user_a,
            date=date(2026, 9, 1),
            time=time(14, 30),
            asset="XAUUSD",
            direction=Direction.BUY,
            timeframe=Timeframe.H1,
            position_size=Decimal("1.50"),
            entry_price=Decimal("2450.50000"),
            result=Result.WIN,
            strategy="Breakout",
            notes="Clean setup",
        )
        self.trade_b = Trade.objects.create(
            user=self.user_b,
            date=date(2026, 9, 2),
            time=time(9, 0),
            asset="EURUSD",
            direction=Direction.SELL,
            timeframe=Timeframe.M15,
            position_size=Decimal("0.50"),
            entry_price=Decimal("1.08453"),
            result=Result.OPEN,
        )

    def test_owner_can_view_their_own_trade(self):
        self.client.login(username="usera", password="SuperSecret123!")
        response = self.client.get(reverse("journal:trade_detail", args=[self.trade_a.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "XAUUSD")

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("journal:trade_detail", args=[self.trade_a.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_user_cannot_view_another_users_trade(self):
        self.client.login(username="usera", password="SuperSecret123!")
        response = self.client.get(reverse("journal:trade_detail", args=[self.trade_b.pk]))
        self.assertEqual(response.status_code, 404)

    def test_nonexistent_trade_returns_404(self):
        self.client.login(username="usera", password="SuperSecret123!")
        response = self.client.get(reverse("journal:trade_detail", args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_page_displays_key_trade_information(self):
        self.client.login(username="usera", password="SuperSecret123!")
        response = self.client.get(reverse("journal:trade_detail", args=[self.trade_a.pk]))
        self.assertContains(response, "XAUUSD")
        self.assertContains(response, "Buy")  # get_direction_display
        self.assertContains(response, "H1")
        self.assertContains(response, "Win")  # get_result_display
        self.assertContains(response, "Breakout")
        self.assertContains(response, "Clean setup")

    def test_optional_empty_fields_show_placeholder(self):
        self.client.login(username="usera", password="SuperSecret123!")
        response = self.client.get(reverse("journal:trade_detail", args=[self.trade_a.pk]))
        # trade_a has no stop_loss/take_profit/exit_price/risk_amount/session/tags
        self.assertContains(response, "—")

    def test_back_to_journal_link_present(self):
        self.client.login(username="usera", password="SuperSecret123!")
        response = self.client.get(reverse("journal:trade_detail", args=[self.trade_a.pk]))
        self.assertContains(response, reverse("journal:index"))


class JournalIndexViewTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username="usera", password="SuperSecret123!")
        self.user_b = User.objects.create_user(username="userb", password="SuperSecret123!")
        self.url = reverse("journal:index")

    def _make_trade(self, user, **overrides):
        defaults = dict(
            user=user,
            date=date(2026, 9, 1),
            time=time(14, 30),
            asset="XAUUSD",
            direction=Direction.BUY,
            timeframe=Timeframe.H1,
            position_size=Decimal("1.50"),
            entry_price=Decimal("2450.50000"),
            result=Result.WIN,
            strategy="Breakout",
        )
        defaults.update(overrides)
        return Trade.objects.create(**defaults)

    def test_authenticated_user_can_access_journal(self):
        self.client.login(username="usera", password="SuperSecret123!")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_user_sees_their_own_trade(self):
        trade = self._make_trade(self.user_a)
        self.client.login(username="usera", password="SuperSecret123!")
        response = self.client.get(self.url)
        self.assertContains(response, "XAUUSD")
        self.assertContains(response, reverse("journal:trade_detail", args=[trade.pk]))

    def test_user_cannot_see_another_users_trade(self):
        self._make_trade(self.user_b, asset="EURUSD")
        self.client.login(username="usera", password="SuperSecret123!")
        response = self.client.get(self.url)
        self.assertNotContains(response, "EURUSD")

    def test_reverse_user_cannot_see_others_trade(self):
        self._make_trade(self.user_a, asset="XAUUSD")
        self.client.login(username="userb", password="SuperSecret123!")
        response = self.client.get(self.url)
        self.assertNotContains(response, "XAUUSD")

    def test_multiple_trades_for_current_user_are_displayed(self):
        self._make_trade(self.user_a, asset="XAUUSD")
        self._make_trade(self.user_a, asset="EURUSD", date=date(2026, 9, 2))
        self.client.login(username="usera", password="SuperSecret123!")
        response = self.client.get(self.url)
        self.assertContains(response, "XAUUSD")
        self.assertContains(response, "EURUSD")

    def test_empty_state_is_displayed_when_no_trades(self):
        self.client.login(username="usera", password="SuperSecret123!")
        response = self.client.get(self.url)
        self.assertContains(response, "No trades yet.")

    def test_trade_link_points_to_actual_pk(self):
        trade = self._make_trade(self.user_a)
        self.client.login(username="usera", password="SuperSecret123!")
        response = self.client.get(self.url)
        expected_url = reverse("journal:trade_detail", args=[trade.pk])
        self.assertContains(response, expected_url)

    def test_add_trade_link_present(self):
        self.client.login(username="usera", password="SuperSecret123!")
        response = self.client.get(self.url)
        self.assertContains(response, reverse("journal:add_trade"))
