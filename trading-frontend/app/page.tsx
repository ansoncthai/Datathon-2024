'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

// Define the type for TradingView widget
interface TradingView {
  widget: (options: {
    width: string | number
    height: string | number
    symbol: string
    interval: string
    timezone: string
    theme: string
    style: string
    locale: string
    toolbar_bg: string
    enable_publishing: boolean
    allow_symbol_change: boolean
    container_id: string
  }) => void
}

export default function BacktestingApp() {
  const [backtestResults, setBacktestResults] = useState({
    totalTrades: 0,
    winRate: 0,
    profitFactor: 0,
    sharpeRatio: 0,
  })

  useEffect(() => {
    // Initialize TradingView widget
    const script = document.createElement('script')
    script.src = 'https://s3.tradingview.com/tv.js'
    script.async = true
    script.onload = () => {
      const tradingView = (window as { TradingView?: TradingView }).TradingView
      if (tradingView?.widget) {
        tradingView.widget({
          width: '100%',
          height: 400,
          symbol: 'NASDAQ:AAPL',
          interval: 'D',
          timezone: 'Etc/UTC',
          theme: 'dark',
          style: '1',
          locale: 'en',
          toolbar_bg: '#f1f3f6',
          enable_publishing: false,
          allow_symbol_change: true,
          container_id: 'tradingview_chart'
        })
      }
    }
    document.head.appendChild(script)

    return () => {
      document.head.removeChild(script)
    }
  }, [])

  const handleBacktest = () => {
    // Simulate backtesting results
    setBacktestResults({
      totalTrades: Math.floor(Math.random() * 1000),
      winRate: Math.random() * 100,
      profitFactor: 1 + Math.random() * 2,
      sharpeRatio: Math.random() * 3,
    })
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-4">
      <h1 className="text-3xl font-bold mb-6 text-center text-gray-800 dark:text-gray-200">Backtesting Trading App</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>TradingView Chart</CardTitle>
            </CardHeader>
            <CardContent>
              <div id="tradingview_chart" className="w-full h-[400px]"></div>
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
                  <p className="text-2xl font-bold">{backtestResults.totalTrades}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Win Rate</p>
                  <p className="text-2xl font-bold">{backtestResults.winRate.toFixed(2)}%</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Profit Factor</p>
                  <p className="text-2xl font-bold">{backtestResults.profitFactor.toFixed(2)}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Sharpe Ratio</p>
                  <p className="text-2xl font-bold">{backtestResults.sharpeRatio.toFixed(2)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Trading Constraints</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="indicator">Indicator</Label>
                <Select>
                  <SelectTrigger id="indicator">
                    <SelectValue placeholder="Select indicator" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="rsi">RSI</SelectItem>
                    <SelectItem value="macd">MACD</SelectItem>
                    <SelectItem value="bollinger">Bollinger Bands</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="condition">Condition</Label>
                <Select>
                  <SelectTrigger id="condition">
                    <SelectValue placeholder="Select condition" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="less_than">&lt;</SelectItem>
                    <SelectItem value="greater_than">&gt;</SelectItem>
                    <SelectItem value="equal_to">=</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="value">Value</Label>
                <Input id="value" type="number" placeholder="Enter value" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="price-condition">Price Condition</Label>
                <Select>
                  <SelectTrigger id="price-condition">
                    <SelectValue placeholder="Select price condition" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="above_sma">Price &gt; SMA</SelectItem>
                    <SelectItem value="below_sma">Price &lt; SMA</SelectItem>
                    <SelectItem value="above_ema">Price &gt; EMA</SelectItem>
                    <SelectItem value="below_ema">Price &lt; EMA</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="ma-period">Moving Average Period</Label>
                <Input id="ma-period" type="number" placeholder="Enter period" />
              </div>
              <Button className="w-full" onClick={handleBacktest}>Run Backtest</Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
