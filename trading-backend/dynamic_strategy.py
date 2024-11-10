from backtesting import Strategy

class DynamicStrategy(Strategy):
    params = {}

    def init(self):
        pass

    def next(self):
        # Check exit conditions first
        if self.position and self.apply_conditions(self.params.get('exits', [])):
            self.position.close()
        # Check entry conditions
        elif not self.position and self.apply_conditions(self.params.get('conditions', [])):
            self.buy()


    def apply_conditions(self, conditions):
        try:
            for condition in conditions:
                indicator = condition.get("indicator")
                period = condition.get("period")
                comparison = condition.get("comparison")
                value = condition.get("value")
                reference = condition.get("reference", None)

                # Get the primary column for the indicator
                column = self.get_indicator_column_name(indicator, period)

                if not column:
                    print(f"Indicator {indicator} not recognized.")
                    return False

                # Check if the column exists
                if not hasattr(self.data, column):
                    print(f"Error: {column} not found in data columns.")
                    return False  # Indicator not calculated or doesn't exist

                # Fetch the indicator value at the current time step
                indicator_value = getattr(self.data, column)[-1]

                # Fetch the reference value
                if reference:
                    reference_value = self.get_reference_value(reference)
                    if reference_value is None:
                        return False
                else:
                    reference_value = value

                # Evaluate the condition
                if not self.evaluate_condition(indicator_value, comparison, reference_value):
                    return False

        except Exception as e:
            print(f"Error applying conditions: {e}")
            return False

        return True

    def get_indicator_column_name(self, indicator, period):
        # Mapping of indicators to their primary column names
        indicator_mapping = {
            "RSI": f"RSI_{period}",
            "SMA": f"SMA_{period}",
            "EMA": f"EMA_{period}",
            "ATR": f"ATR_{period}",
            "CCI": f"CCI_{period}",
            "CMF": f"CMF_{period}",
            "Williams %R": f"Williams_%R_{period}",
            "Donchian Channels": f"DCL_{period}",        # Using the Lower Band as default
            "Parabolic SAR": "PSAR_0.02_0.2",            # Using the default PSAR column
            "MACD": f"MACD_12_26_9",                     # Using the MACD line as default
            # Add more mappings as needed
        }
        return indicator_mapping.get(indicator)

    def get_reference_value(self, reference):
        # Try to get the reference value from indicators or data columns
        if hasattr(self.data, reference):
            return getattr(self.data, reference)[-1]
        else:
            # Attempt to parse the reference as an indicator
            ref_parts = reference.split('_')
            if len(ref_parts) >= 2:
                ref_indicator = ref_parts[0]
                ref_period = int(ref_parts[1]) if ref_parts[1].isdigit() else None
                ref_column = self.get_indicator_column_name(ref_indicator, ref_period)
                if ref_column and hasattr(self.data, ref_column):
                    return getattr(self.data, ref_column)[-1]
            print(f"Reference {reference} not found.")
            return None

    def evaluate_condition(self, indicator_value, comparison, reference_value):
        if comparison == "<":
            return indicator_value < reference_value
        elif comparison == ">":
            return indicator_value > reference_value
        elif comparison == "<=":
            return indicator_value <= reference_value
        elif comparison == ">=":
            return indicator_value >= reference_value
        elif comparison == "==":
            return indicator_value == reference_value
        elif comparison == "!=":
            return indicator_value != reference_value
        else:
            raise ValueError(f"Invalid comparison operator: {comparison}")
