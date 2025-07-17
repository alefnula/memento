from escpos.printer import Network


class ThermalPrinterTester:
    def __init__(self):
        self.printer = Network("192.168.0.220", profile="ITPP047")

    def print_section(self, title):
        """Print section header"""
        self.printer.set(bold=True)
        self.printer.text(f"--- {title} ---\n")
        self.printer.set(bold=False)
        self.printer.text("\n")

    def test_basic_single_lines(self):
        """Test basic single line box drawing"""
        self.print_section("BASIC SINGLE LINES")

        # Small boxes
        self.printer.text("┌─┐ ┌──┐ ┌───┐\n")
        self.printer.text("│ │ │  │ │   │\n")
        self.printer.text("└─┘ └──┘ └───┘\n\n")

        # Character reference
        chars = [
            ("─", "U+2500", "Horizontal"),
            ("│", "U+2502", "Vertical"),
            ("┌", "U+250C", "Top-left"),
            ("┐", "U+2510", "Top-right"),
            ("└", "U+2514", "Bottom-left"),
            ("┘", "U+2518", "Bottom-right"),
            ("┼", "U+253C", "Cross"),
            ("┬", "U+252C", "T-down"),
            ("┴", "U+2534", "T-up"),
            ("├", "U+251C", "T-right"),
            ("┤", "U+2524", "T-left"),
        ]

        for char, code, desc in chars:
            self.printer.text(f"{char} {code} {desc}\n")
        self.printer.text("\n")

    def test_double_lines(self):
        """Test double line characters"""
        self.print_section("DOUBLE LINES")

        self.printer.text("╔═╗ ╔══╗ ╔═══╗\n")
        self.printer.text("║ ║ ║  ║ ║   ║\n")
        self.printer.text("╚═╝ ╚══╝ ╚═══╝\n\n")

        chars = [
            ("═", "U+2550", "Horizontal"),
            ("║", "U+2551", "Vertical"),
            ("╔", "U+2554", "Top-left"),
            ("╗", "U+2557", "Top-right"),
            ("╚", "U+255A", "Bottom-left"),
            ("╝", "U+255D", "Bottom-right"),
            ("╬", "U+256C", "Cross"),
            ("╦", "U+2566", "T-down"),
            ("╩", "U+2569", "T-up"),
            ("╠", "U+2560", "T-right"),
            ("╣", "U+2563", "T-left"),
        ]

        for char, code, desc in chars:
            self.printer.text(f"{char} {code} {desc}\n")
        self.printer.text("\n")

    def test_block_characters(self):
        """Test block and shading characters"""
        self.print_section("BLOCK CHARACTERS")

        chars = [
            ("█", "U+2588", "Full block"),
            ("▓", "U+2593", "Dark shade"),
            ("▒", "U+2592", "Medium shade"),
            ("░", "U+2591", "Light shade"),
            ("▀", "U+2580", "Upper half"),
            ("▄", "U+2584", "Lower half"),
            ("▌", "U+258C", "Left half"),
            ("▐", "U+2590", "Right half"),
        ]

        for char, code, desc in chars:
            self.printer.text(f"{char} {code} {desc}\n")

        self.printer.text("\nShading pattern:\n")
        self.printer.text("█▓▒░█▓▒░█▓▒░█▓▒░\n\n")

    def test_progress_bars(self):
        """Test progress bar examples"""
        self.print_section("PROGRESS BARS")

        self.printer.text("Empty: ░░░░░░░░░░░░\n")
        self.printer.text("25%:   ███░░░░░░░░░\n")
        self.printer.text("50%:   ██████░░░░░░\n")
        self.printer.text("75%:   █████████░░░\n")
        self.printer.text("Full:  ████████████\n\n")

        self.printer.text("Vertical bars:\n")
        self.printer.text("▄ █\n\n")

    def test_receipt_tables(self):
        """Test small tables for receipts"""
        self.print_section("RECEIPT TABLES")

        # Single line receipt table
        self.printer.text("Single line:\n")
        self.printer.text("┌────────────┬─────┬─────┐\n")
        self.printer.text("│ Item       │ Qty │ £   │\n")
        self.printer.text("├────────────┼─────┼─────┤\n")
        self.printer.text("│ Coffee     │  2  │4.50 │\n")
        self.printer.text("│ Sandwich   │  1  │3.25 │\n")
        self.printer.text("├────────────┼─────┼─────┤\n")
        self.printer.text("│ TOTAL      │  3  │7.75 │\n")
        self.printer.text("└────────────┴─────┴─────┘\n\n")

        # Double line for emphasis
        self.printer.text("Double line:\n")
        self.printer.text("╔════════════╦═════╦═════╗\n")
        self.printer.text("║ Product    ║ Qty ║ £   ║\n")
        self.printer.text("╠════════════╬═════╬═════╣\n")
        self.printer.text("║ Tea        ║  1  ║2.50 ║\n")
        self.printer.text("║ Cake       ║  1  ║4.00 ║\n")
        self.printer.text("╠════════════╬═════╬═════╣\n")
        self.printer.text("║ TOTAL      ║  2  ║6.50 ║\n")
        self.printer.text("╚════════════╩═════╩═════╝\n\n")

    def test_patterns(self):
        """Test various patterns"""
        self.print_section("TEST PATTERNS")

        patterns = [
            ("Cross pattern:", "┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼"),
            ("Double cross:", "╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬"),
            ("Shading:", "█▓▒░█▓▒░█▓▒░█▓▒░"),
            ("Double line:", "════════════════"),
        ]

        for name, pattern in patterns:
            self.printer.text(f"{name}\n{pattern}\n\n")

    def run_full_test(self):
        """Run complete test suite"""
        print("Starting thermal printer test...")

        self.test_basic_single_lines()
        self.test_double_lines()
        self.test_block_characters()
        self.test_progress_bars()
        self.test_receipt_tables()
        self.test_patterns()

        print("Test complete! Check your printer output.")

def main():
   tester = ThermalPrinterTester()
   tester.run_full_test()
