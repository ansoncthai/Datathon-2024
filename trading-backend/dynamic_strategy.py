from backtesting import Strategy

class DynamicStrategy(Strategy):
    def init(self):
        pass

    def next(self):
        # Apply user-defined conditions to decide on trades
        self.apply_conditions()

    def apply_conditions(self):
        conditions_met = True

        for condition in self.params.get('conditions', []):
            indicator = condition.get("indicator")
            period = condition.get("period")
            comparison = condition.get("comparison")
            value = condition.get("value")
            reference = condition.get("reference", "Close")  # Default to "Close" if not specified

            # Map indicator names to column names used by the functions
            if indicator == "RSI":
                column = f"RSI_{period}"
            elif indicator == "SMA":
                column = f"SMA_{period}"
            elif indicator == "Bollinger Bands":
                if comparison == "<":
                    column = f"BBL_{period}_{value}"
                elif comparison == ">":
                    column = f"BBU_{period}_{value}"
            elif indicator == "MACD":
                column = "MACD_12_26_9"  # Standard MACD column name
                signal_column = "MACDs_12_26_9"  # MACD signal line column
            elif indicator == "ATR":
                column = f"ATR_{period}"
            elif indicator == "Stochastic Oscillator":
                column = "STOCHk"  # Use the %K line
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
            
            # Get the last value for the condition check
            indicator_value = self.data[column][-1] if column in self.data else None
            reference_value = self.data[reference][-1] if reference in self.data else value

            # Evaluate condition
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
                # Handle missing column case
                conditions_met = False
                break

        # Execute trade based on conditions
        if conditions_met:
            self.buy()
        else:
            self.sell()
