from backtesting import Strategy

class DynamicStrategy(Strategy):
    params = {}

    def init(self):
        pass

    def next(self):
        # Check entry conditions and execute trade if met
        if self.apply_conditions(self.params.get('conditions', [])):
            if not self.position:
                self.buy()
        # Check exit conditions, if defined
        if self.position and self.apply_conditions(self.params.get('exits', [])):
            self.position.close()

    def apply_conditions(self, conditions):
        try:
            for condition in conditions:
                indicator = condition.get("indicator")
                period = condition.get("period")
                comparison = condition.get("comparison")
                value = condition.get("value")
                reference = condition.get("reference", None)

                # Map indicator names to column names
                column = self.get_indicator_column_name(indicator, period)
                # print(f"Applying condition for {indicator} with column {column}")

                # Check if the column exists
                if not hasattr(self.data, column):
                    print(f"Error: {column} not found in data columns.")
                    return False  # Indicator not calculated or doesn't exist

                # Fetch the indicator value at the current time step
                indicator_value = getattr(self.data, column)
                # print(f"Indicator value for {column}: {indicator_value}")

                # Fetch the reference value
                if reference:
                    if hasattr(self.data, reference):
                        reference_value = getattr(self.data, reference)
                    else:
                        # Attempt to calculate the reference indicator
                        ref_parts = reference.split('_')
                        if len(ref_parts) == 2:
                            ref_indicator = ref_parts[0]
                            ref_period = int(ref_parts[1])
                            ref_column = self.get_indicator_column_name(ref_indicator, ref_period)
                            if ref_column and hasattr(self.data, ref_column):
                                reference_value = getattr(self.data, ref_column)
                            else:
                                print(f"Reference indicator {reference} not found.")
                                return False  # Reference indicator not calculated
                        else:
                            print(f"Invalid reference format: {reference}")
                            return False
                else:
                    reference_value = value

                # Evaluate the condition
                if comparison == "<" and not (indicator_value < reference_value):
                    return False
                elif comparison == ">" and not (indicator_value > reference_value):
                    return False
                elif comparison == "<=" and not (indicator_value <= reference_value):
                    return False
                elif comparison == ">=" and not (indicator_value >= reference_value):
                    return False
                elif comparison == "==" and not (indicator_value == reference_value):
                    return False
                elif comparison == "!=" and not (indicator_value != reference_value):
                    return False

        except Exception as e:
            print(f"Error applying conditions: {e}")
            return False

        return True

    def get_indicator_column_name(self, indicator, period):
        # Mapping of indicators to their column names
        indicator_mapping = {
            "RSI": f"RSI_{period}",
            "SMA": f"SMA_{period}",
            "EMA": f"EMA_{period}",
            "ATR": f"ATR_{period}",
            "CCI": f"CCI_{period}",
            "CMF": f"CMF_{period}",
            "Williams %R": f"Williams_%R_{period}",
            "Donchian Channels": f"Donchian_{period}",
            "Parabolic SAR": "PSAR",  # Adjust as necessary
            "MACD": "MACD",           # Adjust as necessary
            # Add more mappings as needed
        }
        return indicator_mapping.get(indicator)
