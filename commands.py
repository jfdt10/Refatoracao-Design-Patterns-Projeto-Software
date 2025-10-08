from abc import ABC, ABCMeta,abstractmethod

class Command(metaclass=ABCMeta):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

class CommandInvoker:
    def __init__(self):
        self._history = []

    def execute_command(self, command: Command):
        try:
            command.execute()
            if getattr(command, "executed", False) or getattr(command, "_executed", False):
                self._history.append(command)
        except Exception as e:
            print(f"Error executing command: {e}")

    def undo_last(self):
        if not self._history:
            print("No commands to undo.")
            return
        command = self._history.pop()
        try:
            command.undo()
        except Exception as e:
            print(f"Error undoing command: {e}")

    def clear_history(self):
        self._history.clear()
        print("Command history cleared.")

    def get_history(self):
        return list(self._history)

class PurchaseProductCommand(Command):
    def __init__(self, product, user=None):
        self.product = product
        self.user = user
        self.executed = False

    def execute(self):
        if self.executed:
            print("PurchaseProductCommand: already executed.")
            return
        if not hasattr(self.product, "purchase_product"):
            print("PurchaseProductCommand: product has no purchase_product method.")
            self.executed = False
            return
        try:
            self.product.purchase_product(self.user)
            self.executed = True
        except Exception as e:
            print(f"PurchaseProductCommand execute error: {e}")
            self.executed = False

    def undo(self):
        if not self.executed:
            print("PurchaseProductCommand: cannot undo, not executed.")
            return
        if not hasattr(self.product, "cancel_purchase"):
            print("PurchaseProductCommand: product has no cancel_purchase method.")
            self.executed = False
            return
        try:
            self.product.cancel_purchase(self.user)
            self.executed = False
        except Exception as e:
            print(f"PurchaseProductCommand undo error: {e}")


class CancelProductCommand(Command):
    def __init__(self, product, user=None):
        self.product = product
        self.user = user
        self.executed = False

    def execute(self):
        if self.executed:
            print("CancelProductCommand: already executed.")
            return
        if not hasattr(self.product, "cancel_purchase"):
            print("CancelProductCommand: product has no cancel_purchase method.")
            self.executed = False
            return
        try:
            self.product.cancel_purchase(self.user)
            self.executed = True
        except Exception as e:
            print(f"CancelProductCommand execute error: {e}")
            self.executed = False

    def undo(self):
        if not self.executed:
            print("CancelProductCommand: cannot undo, not executed.")
            return
        if not hasattr(self.product, "purchase_product"):
            print("CancelProductCommand: product has no purchase_product method.")
            self.executed = False
            return
        try:
            self.product.purchase_product(self.user)
            self.executed = False
        except Exception as e:
            print(f"CancelProductCommand undo error: {e}")


class PurchaseComboCommand(Command):
    def __init__(self, combo, movie, showtime, seat, user, finalize_fn):
        self.combo = combo
        self.movie = movie
        self.showtime = showtime
        self.seat = seat
        self.user = user
        self.finalize_fn = finalize_fn
        self.executed = False
        self._sub_commands = []

    def execute(self):
        if self.executed:
            print("PurchaseComboCommand: already executed.")
            return

        extras = getattr(self.combo, "extras", []) or []
        try:
            for extra in extras:
                cmd = PurchaseProductCommand(extra, self.user)
                cmd.execute()
                if not getattr(cmd, "executed", False):
                    print("PurchaseComboCommand: failed to purchase an extra. Rolling back extras...")
                    for done in reversed(self._sub_commands):
                        try:
                            done.undo()
                        except Exception:
                            pass
                    return
                self._sub_commands.append(cmd)

            try:
                result = None
                try:
                    result = self.finalize_fn(self.combo, self.movie, self.showtime, self.seat)
                except TypeError:
                    try:
                        result = self.finalize_fn(self.combo, self.movie, self.showtime)
                    except Exception:
                        raise
                if result is False:
                    raise RuntimeError("finalize function indicated failure")
            except Exception as e:
                print(f"PurchaseComboCommand: finalize failed: {e}. Rolling back extras...")
                for done in reversed(self._sub_commands):
                    try:
                        done.undo()
                    except Exception:
                        pass
                return

            self.executed = True
        except Exception as e:
            print(f"PurchaseComboCommand execute error: {e}")
            for done in reversed(self._sub_commands):
                try:
                    done.undo()
                except Exception:
                    pass
            self.executed = False

    def undo(self):
        if not self.executed:
            print("PurchaseComboCommand: cannot undo, not executed.")
            return
        try:
            for cmd in reversed(self._sub_commands):
                try:
                    cmd.undo()
                except Exception:
                    pass

            try:
                ticket = getattr(self.combo, "ticket", None)
                if ticket and hasattr(self.user, "cancel_booking"):
                   self.user.cancel_booking(ticket)
            except Exception:
                pass

            try:
                if hasattr(self.seat, "release"):
                    try:
                        self.seat.release(self.user)
                    except TypeError:
                        try:
                            self.seat.release()
                        except Exception:
                            pass
            except Exception:
                pass

            try:
                if self.movie is not None:
                    self.movie.total_tickets_sold = max(0, getattr(self.movie, "total_tickets_sold", 0) - 1)
                    decrement = float(getattr(self.combo, "total_price", 0.0) or 0.0)
                    self.movie.total_revenue = max(0.0, getattr(self.movie, "total_revenue", 0.0) - decrement)
            except Exception:
                pass

            self.executed = False
            print("PurchaseComboCommand: combo purchase undone successfully.")
        except Exception as e:
            print(f"PurchaseComboCommand undo error: {e}")