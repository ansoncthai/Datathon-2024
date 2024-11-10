'use client'

import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { PlusCircle, Trash2 } from 'lucide-react'

import { createChart, CrosshairMode, SeriesMarker, SeriesMarkerPosition, SeriesMarkerShape, Time } from 'lightweight-charts'

const getTodayDate = () => {
    const today = new Date();
    return today.toLocaleDateString('en-CA');
}

type Condition = {
    indicator: string
    period: number
    comparison: string
    reference?: string
    value?: number
}

type BacktestParams = {
    ticker: string
    start_date: string
    end_date: string
    params: {
        conditions: Condition[]
        exits: Condition[]
    }
    initial_cash: number
    commission: number
}

export default function BacktestingApp() {
    const [backtestParams, setBacktestParams] = useState<BacktestParams>({
        ticker: 'enter value',
        start_date: getTodayDate(),
        end_date: getTodayDate(),
        params: {
            conditions: [
                { indicator: 'SMA', period: 20, comparison: '>', reference: 'SMA_50' },
                { indicator: 'RSI', period: 14, comparison: '<', value: 30 }
            ],
            exits: [
                { indicator: 'SMA', period: 20, comparison: '<', reference: 'SMA_50' },
                { indicator: 'RSI', period: 14, comparison: '>', value: 70 }
            ]
        },
        initial_cash: 10000,
        commission: 0.002
    })

    // Hardcoded backtest results based on your payload
    const [backtestResults] = useState({
        max_drawdown: "N/A",
        profit_factor: NaN,
        sharpe_ratio: 0.8873656123089387,
        total_return: 39.43077330841064,
        trade_history: [
            {
                "Duration": 172800.0,
                "EntryBar": 104,
                "EntryPrice": 43.98780152893067,
                "EntryTime": "2019-06-03",
                "ExitBar": 106,
                "ExitPrice": 46.06999969482422,
                "ExitTime": "2019-06-05",
                "PnL": 472.65898365783613,
                "ReturnPct": 0.04733580887246869,
                "Size": 227
            },
            {
                "Duration": 345600.0,
                "EntryBar": 291,
                "EntryPrice": 64.44363244628906,
                "EntryTime": "2020-02-28",
                "ExitBar": 293,
                "ExitPrice": 75.9175033569336,
                "ExitTime": "2020-03-03",
                "PnL": 1858.7670875244148,
                "ReturnPct": 0.17804506783827723,
                "Size": 162
            },
            // ... Include other trades from your payload
        ],
        win_rate: 100.0
    })

    const chartContainerRef = useRef(null)

    useEffect(() => {
        // Initialize the chart with hardcoded data
        if (chartContainerRef.current) {
            const chart = createChart(chartContainerRef.current, {
                width: chartContainerRef.current.clientWidth,
                height: 400,
                layout: {
                    background: { color: '#FFFFFF' },
                    textColor: '#000000',
                },
                grid: {
                    vertLines: {
                        color: '#e0e0e0',
                    },
                    horzLines: {
                        color: '#e0e0e0',
                    },
                },
                crosshair: {
                    mode: CrosshairMode.Normal,
                },
                timeScale: {
                    timeVisible: true,
                    secondsVisible: false,
                },
            })

            const candleSeries = chart.addCandlestickSeries()

            // Hardcoded price data (simplified example)

            const priceData = [
                { time: '2019-06-03', open: 43.87, high: 44.00, low: 43.50, close: 43.98 },
                { time: '2019-06-04', open: 44.00, high: 45.00, low: 43.90, close: 44.50 },
                { time: '2019-06-05', open: 44.50, high: 46.50, low: 44.20, close: 46.07 },
                { time: '2019-06-06', open: 46.07, high: 47.00, low: 45.50, close: 46.50 },
                { time: '2019-06-07', open: 46.50, high: 47.20, low: 46.00, close: 46.70 },
                { time: '2019-06-10', open: 46.70, high: 47.80, low: 46.50, close: 47.20 },
                { time: '2019-06-11', open: 47.20, high: 47.90, low: 46.90, close: 47.50 },
                { time: '2019-06-12', open: 47.50, high: 48.20, low: 47.00, close: 47.80 },
                { time: '2019-06-13', open: 47.80, high: 48.50, low: 47.40, close: 48.00 },
                { time: '2019-06-14', open: 48.00, high: 48.50, low: 47.60, close: 47.90 },
                { time: '2019-06-17', open: 47.90, high: 48.10, low: 47.20, close: 47.70 },
                { time: '2019-06-18', open: 47.70, high: 48.50, low: 47.60, close: 48.20 },
                { time: '2019-06-19', open: 48.20, high: 49.00, low: 48.10, close: 48.90 },
                { time: '2019-06-20', open: 48.90, high: 49.50, low: 48.60, close: 49.00 },
                { time: '2020-02-28', open: 62.00, high: 65.00, low: 61.50, close: 64.44 },
                { time: '2020-03-02', open: 65.00, high: 68.00, low: 64.00, close: 67.00 },
                { time: '2020-03-03', open: 67.00, high: 76.00, low: 66.00, close: 75.92 },
                { time: '2020-03-04', open: 75.92, high: 77.00, low: 75.00, close: 76.50 },
                { time: '2020-03-05', open: 76.50, high: 78.00, low: 75.80, close: 77.20 },
                { time: '2020-03-06', open: 77.20, high: 79.00, low: 76.50, close: 78.00 },
                // ... add more data points as needed
            ]
            
            candleSeries.setData(priceData)

            // Prepare markers from trade history
            const markers: SeriesMarker<Time>[] = backtestResults.trade_history.flatMap(trade => {
                const entryMarker: SeriesMarker<Time> = {
                    time: trade.EntryTime as Time,
                    position: 'belowBar',
                    color: 'green',
                    shape: 'arrowUp',
                    text: `Buy @ ${trade.EntryPrice.toFixed(2)}`,
                }
                const exitMarker: SeriesMarker<Time> = {
                    time: trade.ExitTime as Time,
                    position: 'aboveBar',
                    color: 'red',
                    shape: 'arrowDown',
                    text: `Sell @ ${trade.ExitPrice.toFixed(2)}`,
                }
                return [entryMarker, exitMarker]
            })

            candleSeries.setMarkers(markers)

            // Cleanup on unmount
            return () => {
                chart.remove()
            }
        }
    }, [backtestResults.trade_history])

    const updateCondition = (index: number, field: keyof Condition, value: string | number, isExit: boolean) => {
        const paramType = isExit ? 'exits' : 'conditions'
        setBacktestParams(prev => ({
            ...prev,
            params: {
                ...prev.params,
                [paramType]: prev.params[paramType].map((condition, i) =>
                    i === index ? { ...condition, [field]: value } : condition
                )
            }
        }))
    }

    const addCondition = (isExit: boolean) => {
        const paramType = isExit ? 'exits' : 'conditions'
        setBacktestParams(prev => ({
            ...prev,
            params: {
                ...prev.params,
                [paramType]: [...prev.params[paramType], { indicator: 'SMA', period: 20, comparison: '>' }]
            }
        }))
    }

    const removeCondition = (index: number, isExit: boolean) => {
        const paramType = isExit ? 'exits' : 'conditions'
        setBacktestParams(prev => ({
            ...prev,
            params: {
                ...prev.params,
                [paramType]: prev.params[paramType].filter((_, i) => i !== index)
            }
        }))
    }

    const handleBacktest = () => {
        // Implement the backtest logic here
        // For now, we'll just log the parameters
        console.log('Running backtest with params:', backtestParams)
    }

    const renderConditionInputs = (condition: Condition, index: number, isExit: boolean) => (
        <div key={index} className="space-y-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <div className="flex justify-between items-center">
                <Label>{isExit ? 'Exit Condition' : 'Entry Condition'} {index + 1}</Label>
                <Button variant="ghost" size="icon" onClick={() => removeCondition(index, isExit)}>
                    <Trash2 className="h-4 w-4" />
                </Button>
            </div>
            <div className="space-y-2">
                <Select value={condition.indicator} onValueChange={(value) => updateCondition(index, 'indicator', value, isExit)}>
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
                    value={condition.period}
                    onChange={(e) => updateCondition(index, 'period', parseInt(e.target.value) || 0, isExit)}
                />
                <Select value={condition.comparison} onValueChange={(value) => updateCondition(index, 'comparison', value, isExit)}>
                    <SelectTrigger>
                        <SelectValue placeholder="Select comparison" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value=">">&gt;</SelectItem>
                        <SelectItem value="<">&lt;</SelectItem>
                        <SelectItem value="=">=</SelectItem>
                    </SelectContent>
                </Select>
                {condition.value !== undefined ? (
                    <Input
                        type="number"
                        placeholder="Value"
                        value={condition.value}
                        onChange={(e) => updateCondition(index, 'value', parseFloat(e.target.value) || 0, isExit)}
                    />
                ) : (
                    <Input
                        type="text"
                        placeholder="Reference (e.g., Close, SMA_50)"
                        value={condition.reference || ''}
                        onChange={(e) => updateCondition(index, 'reference', e.target.value, isExit)}
                    />
                )}
            </div>
        </div>
    )

    // Calculate total trades
    const totalTrades = backtestResults.trade_history.length

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-4">
            <h1 className="text-3xl font-bold mb-6 text-center text-gray-800 dark:text-gray-200">Backtesting Trading App</h1>
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
                                        onChange={(e) => setBacktestParams(prev => ({ ...prev, ticker: e.target.value }))}
                                    />
                                </div>
                                <div className="flex flex-col space-y-1">
                                    <Label htmlFor="start_date">Start Date</Label>
                                    <Input
                                        id="start_date"
                                        type="date"
                                        value={backtestParams.start_date}
                                        onChange={(e) => setBacktestParams(prev => ({ ...prev, start_date: e.target.value }))}
                                    />
                                </div>
                                <div className="flex flex-col space-y-1">
                                    <Label htmlFor="end_date">End Date</Label>
                                    <Input
                                        id="end_date"
                                        type="date"
                                        value={backtestParams.end_date}
                                        onChange={(e) => setBacktestParams(prev => ({ ...prev, end_date: e.target.value }))}
                                    />
                                </div>
                                <div className="flex flex-col space-y-1">
                                    <Label htmlFor="initial_cash">Initial Cash</Label>
                                    <Input
                                        id="initial_cash"
                                        type="number"
                                        value={backtestParams.initial_cash}
                                        onChange={(e) => setBacktestParams(prev => ({ ...prev, initial_cash: parseFloat(e.target.value) || 0 }))}
                                    />
                                </div>
                                <div className="flex flex-col space-y-1">
                                    <Label htmlFor="commission">Commission</Label>
                                    <Input
                                        id="commission"
                                        type="number"
                                        step="0.001"
                                        value={backtestParams.commission}
                                        onChange={(e) => setBacktestParams(prev => ({ ...prev, commission: parseFloat(e.target.value) || 0 }))}
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
                                <div ref={chartContainerRef} id="tradingview_chart" className="w-full h-[400px]"></div>
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
                                        <p className="text-2xl font-bold">{totalTrades}</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-sm text-gray-500 dark:text-gray-400">Win Rate</p>
                                        <p className="text-2xl font-bold">{backtestResults.win_rate.toFixed(2)}%</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-sm text-gray-500 dark:text-gray-400">Profit Factor</p>
                                        <p className="text-2xl font-bold">{isNaN(backtestResults.profit_factor) ? 'N/A' : backtestResults.profit_factor.toFixed(2)}</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-sm text-gray-500 dark:text-gray-400">Sharpe Ratio</p>
                                        <p className="text-2xl font-bold">{backtestResults.sharpe_ratio.toFixed(2)}</p>
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
                                    <Button type="button" variant="outline" className="w-full" onClick={() => addCondition(false)}>
                                        <PlusCircle className="mr-2 h-4 w-4" /> Add Entry Condition
                                    </Button>
                                </div>
                                <div className="space-y-2">
                                    <Label>Exit Conditions</Label>
                                    {backtestParams.params.exits.map((exit, index) =>
                                        renderConditionInputs(exit, index, true)
                                    )}
                                    <Button type="button" variant="outline" className="w-full" onClick={() => addCondition(true)}>
                                        <PlusCircle className="mr-2 h-4 w-4" /> Add Exit Condition
                                    </Button>
                                </div>
                                <Button type="button" className="w-full" onClick={handleBacktest}>Run Backtest</Button>
                            </form>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}