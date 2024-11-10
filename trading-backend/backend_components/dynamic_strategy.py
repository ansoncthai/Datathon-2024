from backtesting import Strategy

class DynamicStrategy(Strategy):
    def init(self):
        # No need to initialize indicators here; they are precomputed in the DataFrame.
        pass

    def next(self):
        # Apply user-defined conditions to decide on trades
        self.apply_conditions()

    def apply_conditions(self):
        conditions_met = True  # Assume all conditions are met initially

        # Loop through each condition from the user's input
        for condition in self.params.get('conditions', []):
            indicator = condition.get("indicator")
            period = condition.get("period")
            comparison = condition.get("comparison")
            value = condition.get("value")
            reference = condition.get("reference", "Close")  # Default to compare against "Close" if not specified

            # Retrieve the relevant column name based on indicator and period
            if indicator == "RSI":
                column = f"RSI_{period}"
            elif indicator == "SMA":
                column = f"SMA_{period}"
            elif indicator == "Bollinger Bands":
                if comparison == "<":
                    column = f"BBL_{period}_{value}"  # Lower band for comparison
                elif comparison == ">":
                    column = f"BBU_{period}_{value}"  # Upper band for comparison
            elif indicator == "MACD":
                column = "MACD_12_26_9"  # Assuming a standard MACD setup
                signal_column = "MACDs_12_26_9"  # MACD signal line
            elif indicator == "ATR":
                column = f"ATR_{period}"
            elif indicator == "Stochastic Oscillator":
                column = "STOCHk"  # Assuming we're using the %K line for simplicity
            elif indicator == "OBV":
                column = "OBV"
            elif indicator == "CMF":
                column = f"CMF_{period}"
            elif indicator == "Williams %R":
                column = f"Williams_%R_{period}"
            elif indicator == "CCI":
                column = f"CCI_{period}"
            elif indicator == "Parabolic SAR":
                column = "Parabolic_SAR"

            # Get the indicator value from the last available data point
            indicator_value = self.data[column][-1] if column in self.data else None
            reference_value = self.data[reference][-1] if reference in self.data else value

            # If any condition fails, set conditions_met to False and break out
            if indicator_value is not None:
                if comparison == "<" and not (indicator_value < reference_value):
                    conditions_met = False
                    break
                elif comparison == ">" and not (indicator_value > reference_value):
                    conditions_met = False
                    break
                elif comparison == "<=" and not (indicator_value <= reference_value):
                    conditions_met = False
                    break
                elif comparison == ">=" and not (indicator_value >= reference_value):
                    conditions_met = False
                    break
                elif comparison == "==" and not (indicator_value == reference_value):
                    conditions_met = False
                    break
            else:
                # If the column is missing, log or handle the missing data case
                conditions_met = False
                break

        # Execute trade based on whether all conditions are met
        if conditions_met:
            self.buy()
        else:
            self.sell()
