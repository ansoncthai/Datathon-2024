'use client';

import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { PlusCircle, Trash2 } from 'lucide-react';

import {
    createChart,
    IChartApi,
    CrosshairMode,
    SeriesMarker,
    Time,
} from 'lightweight-charts';

const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0]; // 'YYYY-MM-DD'
};

type Condition = {
    indicator: string;
    period: number;
    comparison: string;
    reference?: string;
    value?: number;
};

type BacktestParams = {
    ticker: string;
    start_date: string;
    end_date: string;
    params: {
        conditions: Condition[];
        exits: Condition[];
    };
    initial_cash: number;
    commission: number;
};

type PriceDataItem = {
    date: string; // 'YYYY-MM-DD' format
    open: number;
    high: number;
    low: number;
    close: number;
};

type TradeHistoryEntry = {
    Duration: number;
    EntryBar: number;
    EntryPrice: number;
    EntryTime: string;
    ExitBar: number;
    ExitPrice: number;
    ExitTime: string;
    PnL: number;
    ReturnPct: number;
    Size: number;
};

export default function BacktestingApp() {
    const [backtestParams, setBacktestParams] = useState<BacktestParams>({
        ticker: '',
        start_date: '',
        end_date: '',
        params: {
            conditions: [],
            exits: [],
        },
        initial_cash: 10000,
        commission: 0.002,
    });

    const [backtestResults, setBacktestResults] = useState<{
        max_drawdown: string | number;
        profit_factor: number;
        sharpe_ratio: number;
        total_return: number;
        trade_history: TradeHistoryEntry[];
        win_rate: number;
    }>({
        max_drawdown: 'N/A',
        profit_factor: NaN,
        sharpe_ratio: NaN,
        total_return: NaN,
        trade_history: [],
        win_rate: NaN,
    });

    const chartContainerRef = useRef<HTMLDivElement | null>(null);

    const [fetchError, setFetchError] = useState<string | null>(null);

    useEffect(() => {
        let chart: IChartApi | null = null;

        const fetchDataAndRenderChart = async () => {
            if (
                chartContainerRef.current &&
                backtestParams.ticker &&
                backtestParams.start_date &&
                backtestParams.end_date
            ) {
                try {
                    // Initialize the chart
                    chart = createChart(chartContainerRef.current, {
                        width: chartContainerRef.current.clientWidth,
                        height: 400,
                        layout: {
                            background: { color: '#FFFFFF' },
                            textColor: '#000000',
                        },
                        grid: {
                            vertLines: { color: '#e0e0e0' },
                            horzLines: { color: '#e0e0e0' },
                        },
                        crosshair: {
                            mode: CrosshairMode.Normal,
                        },
                        timeScale: {
                            timeVisible: true,
                            secondsVisible: false,
                        },
                    });

                    const candleSeries = chart.addCandlestickSeries();

                    // Fetch price data
                    const url = `http://127.0.0.1:5000/api/get-price-data?ticker=${encodeURIComponent(backtestParams.ticker)}&start_date=${encodeURIComponent(backtestParams.start_date)}&end_date=${encodeURIComponent(backtestParams.end_date)}`;
                    console.log('Fetching price data from:', url);

                    const response = await fetch(url);

                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.error || 'Error fetching price data');
                    }

                    const data: PriceDataItem[] = await response.json();
                    console.log('Received price data:', data);

                    if (data.length === 0) {
                        throw new Error('No price data available for the selected ticker and date range.');
                    }

                    // Format price data
                    const priceData = data.map((item: PriceDataItem) => ({
                        time: item.date as Time,
                        open: item.open,
                        high: item.high,
                        low: item.low,
                        close: item.close,
                    }));

                    candleSeries.setData(priceData);

                    // Prepare markers if trade history is available
                    if (backtestResults.trade_history && backtestResults.trade_history.length > 0) {
                        const markers: SeriesMarker<Time>[] = backtestResults.trade_history.flatMap(
                            (trade: TradeHistoryEntry) => {
                                const entryTime = trade.EntryTime.split('T')[0];
                                const exitTime = trade.ExitTime ? trade.ExitTime.split('T')[0] : null;

                                const markersList: SeriesMarker<Time>[] = [
                                    {
                                        time: entryTime as Time,
                                        position: 'belowBar',
                                        color: 'green',
                                        shape: 'arrowUp',
                                        text: `Buy @ ${trade.EntryPrice.toFixed(2)}`,
                                    },
                                ];

                                if (exitTime) {
                                    markersList.push({
                                        time: exitTime as Time,
                                        position: 'aboveBar',
                                        color: 'red',
                                        shape: 'arrowDown',
                                        text: `Sell @ ${trade.ExitPrice.toFixed(2)}`,
                                    });
                                }

                                return markersList;
                            }
                        );

                        candleSeries.setMarkers(markers);
                    }

                    chart.timeScale().fitContent();
                } catch (error: any) {
                    console.error('Error fetching price data:', error);
                    setFetchError(error.message || 'Error fetching price data');
                }
            } else {
                console.log('Chart container or backtest parameters not set.');
            }
        };

        fetchDataAndRenderChart();

        // Cleanup on unmount
        return () => {
            if (chart) {
                chart.remove();
            }
        };
    }, [backtestResults, backtestParams]);

    const updateCondition = (
        index: number,
        field: keyof Condition,
        value: string | number,
        isExit: boolean
    ) => {
        const paramType = isExit ? 'exits' : 'conditions';
        setBacktestParams((prev) => ({
            ...prev,
            params: {
                ...prev.params,
                [paramType]: prev.params[paramType].map((condition, i) =>
                    i === index ? { ...condition, [field]: value } : condition
                ),
            },
        }));
    };

    const addCondition = (isExit: boolean) => {
        const paramType = isExit ? 'exits' : 'conditions';
        setBacktestParams((prev) => ({
            ...prev,
            params: {
                ...prev.params,
                [paramType]: [
                    ...prev.params[paramType],
                    { indicator: '', period: 0, comparison: '', reference: '' }, // Added reference as empty
                ],
            },
        }));
    };

    const removeCondition = (index: number, isExit: boolean) => {
        const paramType = isExit ? 'exits' : 'conditions';
        setBacktestParams((prev) => ({
            ...prev,
            params: {
                ...prev.params,
                [paramType]: prev.params[paramType].filter((_, i) => i !== index),
            },
        }));
    };

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleBacktest = async () => {
        console.log('Backtest parameters:', backtestParams);
        setLoading(true);
        setError(null);

        // Input validation before making the request
        if (!backtestParams.ticker || !backtestParams.start_date || !backtestParams.end_date) {
            setError('Please enter the ticker, start date, and end date.');
            setLoading(false);
            return;
        }

        if (
            backtestParams.params.conditions.length === 0 ||
            backtestParams.params.exits.length === 0
        ) {
            setError('Please add at least one entry and one exit condition.');
            setLoading(false);
            return;
        }

        try {
            const url = 'http://127.0.0.1:5000/api/run-backtest';
            console.log('Sending backtest request to:', url);

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(backtestParams),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error running backtest');
            }

            const data = await response.json();
            console.log('Backtest results:', data);
            setBacktestResults(data);
            setFetchError(null); // Clear any previous fetch errors
        } catch (err: any) {
            console.error('Error running backtest:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const renderConditionInputs = (
        condition: Condition,
        index: number,
        isExit: boolean
    ) => (
        <div
            key={index}
            className="space-y-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg"
        >
            <div className="flex justify-between items-center">
                <Label>
                    {isExit ? 'Exit Condition' : 'Entry Condition'} {index + 1}
                </Label>
                <Button variant="ghost" size="icon" onClick={() => removeCondition(index, isExit)}>
                    <Trash2 className="h-4 w-4" />
                </Button>
            </div>
            <div className="space-y-2">
                <Select
                    value={condition.indicator}
                    onValueChange={(value) =>
                        updateCondition(index, 'indicator', value, isExit)
                    }
                >
                    <SelectTrigger>
                        <SelectValue placeholder="Select indicator" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="SMA">SMA</SelectItem>
                        <SelectItem value="EMA">EMA</SelectItem>
                        <SelectItem value="RSI">RSI</SelectItem>
                        {/* Add more indicators as needed */}
                    </SelectContent>
                </Select>
                <Input
                    type="number"
                    placeholder="Period"
                    value={condition.period || ''}
                    onChange={(e) =>
                        updateCondition(
                            index,
                            'period',
                            parseInt(e.target.value) || 0,
                            isExit
                        )
                    }
                />
                <Select
                    value={condition.comparison}
                    onValueChange={(value) =>
                        updateCondition(index, 'comparison', value, isExit)
                    }
                >
                    <SelectTrigger>
                        <SelectValue placeholder="Select comparison" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value=">">&gt;</SelectItem>
                        <SelectItem value="<">&lt;</SelectItem>
                        <SelectItem value="=">=</SelectItem>
                    </SelectContent>
                </Select>
                {condition.indicator === 'RSI' ? (
                    <Input
                        type="number"
                        placeholder="Value"
                        value={condition.value || ''}
                        onChange={(e) =>
                            updateCondition(
                                index,
                                'value',
                                parseFloat(e.target.value) || 0,
                                isExit
                            )
                        }
                    />
                ) : (
                    <Input
                        type="text"
                        placeholder="Reference (e.g., SMA_50)"
                        value={condition.reference || ''}
                        onChange={(e) => updateCondition(index, 'reference', e.target.value, isExit)}
                    />
                )}
            </div>
        </div>
    );

    // Calculate total trades
    const totalTrades = backtestResults.trade_history.length;

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-4">
            <h1 className="text-3xl font-bold mb-6 text-center text-gray-800 dark:text-gray-200">
                Backtesting Trading App
            </h1>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-2">
                    <Card>
                        <CardHeader>
                            <CardTitle>Backtest Parameters</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <form className="space-y-4 grid grid-cols-2 gap-4">
                                <div className="flex flex-col space-y-1">
                                    <Label htmlFor="ticker">Ticker</Label>
                                    <Input
                                        id="ticker"
                                        value={backtestParams.ticker}
                                        onChange={(e) =>
                                            setBacktestParams((prev) => ({
                                                ...prev,
                                                ticker: e.target.value,
                                            }))
                                        }
                                        placeholder="e.g., AAPL"
                                    />
                                </div>
                                <div className="flex flex-col space-y-1">
                                    <Label htmlFor="start_date">Start Date</Label>
                                    <Input
                                        id="start_date"
                                        type="date"
                                        value={backtestParams.start_date}
                                        onChange={(e) =>
                                            setBacktestParams((prev) => ({
                                                ...prev,
                                                start_date: e.target.value,
                                            }))
                                        }
                                    />
                                </div>
                                <div className="flex flex-col space-y-1">
                                    <Label htmlFor="end_date">End Date</Label>
                                    <Input
                                        id="end_date"
                                        type="date"
                                        value={backtestParams.end_date}
                                        onChange={(e) =>
                                            setBacktestParams((prev) => ({
                                                ...prev,
                                                end_date: e.target.value,
                                            }))
                                        }
                                    />
                                </div>
                                <div className="flex flex-col space-y-1">
                                    <Label htmlFor="initial_cash">Initial Cash</Label>
                                    <Input
                                        id="initial_cash"
                                        type="number"
                                        value={backtestParams.initial_cash}
                                        onChange={(e) =>
                                            setBacktestParams((prev) => ({
                                                ...prev,
                                                initial_cash: parseFloat(e.target.value) || 0,
                                            }))
                                        }
                                        placeholder="e.g., 10000"
                                    />
                                </div>
                                <div className="flex flex-col space-y-1">
                                    <Label htmlFor="commission">Commission</Label>
                                    <Input
                                        id="commission"
                                        type="number"
                                        step="0.001"
                                        value={backtestParams.commission}
                                        onChange={(e) =>
                                            setBacktestParams((prev) => ({
                                                ...prev,
                                                commission: parseFloat(e.target.value) || 0,
                                            }))
                                        }
                                        placeholder="e.g., 0.002"
                                    />
                                </div>
                            </form>
                        </CardContent>
                    </Card>
                    <div className="lg:col-span-2 space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>Trading Chart</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div
                                    ref={chartContainerRef}
                                    id="tradingview_chart"
                                    className="w-full h-[400px]"
                                ></div>
                                {fetchError && (
                                    <p className="text-red-500 text-center mt-2">{fetchError}</p>
                                )}
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader>
                                <CardTitle>Backtesting Statistics</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="text-center">
                                        <p className="text-sm text-gray-500 dark:text-gray-400">Total Trades</p>
                                        <p className="text-2xl font-bold">
                                            {isNaN(totalTrades) ? 'N/A' : totalTrades}
                                        </p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-sm text-gray-500 dark:text-gray-400">Win Rate</p>
                                        <p className="text-2xl font-bold">
                                            {isNaN(backtestResults.win_rate)
                                                ? 'N/A'
                                                : `${parseFloat(backtestResults.win_rate.toString()).toFixed(2)}%`}
                                        </p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-sm text-gray-500 dark:text-gray-400">Profit Factor</p>
                                        <p className="text-2xl font-bold">
                                            {isNaN(backtestResults.profit_factor)
                                                ? 'N/A'
                                                : backtestResults.profit_factor.toFixed(2)}
                                        </p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-sm text-gray-500 dark:text-gray-400">Sharpe Ratio</p>
                                        <p className="text-2xl font-bold">
                                            {isNaN(backtestResults.sharpe_ratio)
                                                ? 'N/A'
                                                : backtestResults.sharpe_ratio.toFixed(2)}
                                        </p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>

                <div className="lg:col-span-1">
                    <Card>
                        <CardHeader>
                            <CardTitle>Conditions</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <form className="space-y-4">
                                <div className="space-y-2">
                                    <Label>Entry Conditions</Label>
                                    {backtestParams.params.conditions.map((condition, index) =>
                                        renderConditionInputs(condition, index, false)
                                    )}
                                    <Button
                                        type="button"
                                        variant="outline"
                                        className="w-full"
                                        onClick={() => addCondition(false)}
                                    >
                                        <PlusCircle className="mr-2 h-4 w-4" /> Add Entry Condition
                                    </Button>
                                </div>
                                <div className="space-y-2">
                                    <Label>Exit Conditions</Label>
                                    {backtestParams.params.exits.map((exit, index) =>
                                        renderConditionInputs(exit, index, true)
                                    )}
                                    <Button
                                        type="button"
                                        variant="outline"
                                        className="w-full"
                                        onClick={() => addCondition(true)}
                                    >
                                        <PlusCircle className="mr-2 h-4 w-4" /> Add Exit Condition
                                    </Button>
                                </div>
                                <Button type="button" className="w-full" onClick={handleBacktest} disabled={loading}>
                                    {loading ? 'Running Backtest...' : 'Run Backtest'}
                                </Button>
                                {error && <p className="text-red-500 text-center">{error}</p>}
                            </form>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}