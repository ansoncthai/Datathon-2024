from backtesting import Strategy

class DynamicStrategy(Strategy):
    params = {}

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
                else:
                    conditions_met = False
                    break
            elif indicator == "MACD":
                column = "MACD_12_26_9"  # Standard MACD column name
                signal_column = "MACDs_12_26_9"  # MACD signal line column
            elif indicator == "ATR":
                column = f"ATR_{period}"
            elif indicator == "Stochastic Oscillator":
                column = "STOCHk_14_3_3"  # Adjust as per your calculation
            elif indicator == "OBV":
                column = "OBV"
            elif indicator == "CMF":
                column = f"CMF_{period}"
            elif indicator == "Williams %R":
                column = f"Williams_%R_{period}"
            elif indicator == "CCI":
                column = f"CCI_{period}"
            elif indicator == "Parabolic SAR":
                column = "PSARl_0.02_0.2"  # Adjust as per your calculation
            else:
                # Unsupported indicator
                conditions_met = False
                break

            # Get the last value for the condition check
            indicator_value = self.data.df[column].iloc[-1] if column in self.data.df.columns else None
            reference_value = self.data.df[reference].iloc[-1] if reference in self.data.df.columns else value

            # Evaluate condition
            if indicator_value is not None and reference_value is not None:
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
                # Handle missing column or reference value
                conditions_met = False
                break

        # Execute trade based on conditions
        if conditions_met:
            if not self.position:
                self.buy()
        else:
            if self.position:
                self.position.close()
