'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { PlusCircle, Trash2 } from 'lucide-react'

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
    ticker: 'TSLA',
    start_date: '2019-01-01',
    end_date: '2023-12-31',
    params: {
      conditions: [{ indicator: 'SMA', period: 20, comparison: '>', reference: 'SMA_50' }],
      exits: [{ indicator: 'SMA', period: 20, comparison: '<', reference: 'SMA_50' }]
    },
    initial_cash: 10000,
    commission: 0.002
  })

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
      new (window as any).TradingView.widget({
        width: '100%',
        height: 400,
        symbol: 'NASDAQ:TSLA',
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
    document.head.appendChild(script)

    return () => {
      document.head.removeChild(script)
    }
  }, [])

  const handleBacktest = async () => {
    try {
      // Simulating API call
      const response = await fetch('/api/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(backtestParams)
      })
      const data = await response.json()
      setBacktestResults(data)
    } catch (error) {
      console.error('Error running backtest:', error)
      // Handle error (e.g., show error message to user)
    }
  }

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

  const renderConditionInputs = (condition: Condition, index: number, isExit: boolean) => (
    <div key={index} className="space-y-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
      <div className="flex justify-between items-center">
        <Label>Condition {index + 1}</Label>
        <Button variant="ghost" size="icon" onClick={() => removeCondition(index, isExit)}>
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
      <Select value={condition.indicator} onValueChange={(value) => updateCondition(index, 'indicator', value, isExit)}>
        <SelectTrigger>
          <SelectValue placeholder="Select indicator" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="SMA">SMA</SelectItem>
          <SelectItem value="EMA">EMA</SelectItem>
          <SelectItem value="RSI">RSI</SelectItem>
        </SelectContent>
      </Select>
      <Input 
        type="number" 
        placeholder="Period" 
        value={condition.period} 
        onChange={(e) => updateCondition(index, 'period', parseInt(e.target.value), isExit)}
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
      {condition.indicator === 'RSI' ? (
        <Input 
          type="number" 
          placeholder="Value" 
          value={condition.value || ''} 
          onChange={(e) => updateCondition(index, 'value', parseFloat(e.target.value), isExit)}
        />
      ) : (
        <Select value={condition.reference} onValueChange={(value) => updateCondition(index, 'reference', value, isExit)}>
          <SelectTrigger>
            <SelectValue placeholder="Select reference" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="SMA_50">SMA 50</SelectItem>
            <SelectItem value="SMA_200">SMA 200</SelectItem>
            <SelectItem value="EMA_50">EMA 50</SelectItem>
            <SelectItem value="EMA_200">EMA 200</SelectItem>
          </SelectContent>
        </Select>
      )}
    </div>
  )

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
            <CardTitle>Backtest Parameters</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="ticker">Ticker</Label>
                <Input 
                  id="ticker" 
                  value={backtestParams.ticker} 
                  onChange={(e) => setBacktestParams(prev => ({ ...prev, ticker: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="start_date">Start Date</Label>
                <Input 
                  id="start_date" 
                  type="date" 
                  value={backtestParams.start_date} 
                  onChange={(e) => setBacktestParams(prev => ({ ...prev, start_date: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end_date">End Date</Label>
                <Input 
                  id="end_date" 
                  type="date" 
                  value={backtestParams.end_date} 
                  onChange={(e) => setBacktestParams(prev => ({ ...prev, end_date: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="initial_cash">Initial Cash</Label>
                <Input 
                  id="initial_cash" 
                  type="number" 
                  value={backtestParams.initial_cash} 
                  onChange={(e) => setBacktestParams(prev => ({ ...prev, initial_cash: parseFloat(e.target.value) }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="commission">Commission</Label>
                <Input 
                  id="commission" 
                  type="number" 
                  step="0.001" 
                  value={backtestParams.commission} 
                  onChange={(e) => setBacktestParams(prev => ({ ...prev, commission: parseFloat(e.target.value) }))}
                />
              </div>
              <div className="space-y-2">
                <Label>Entry Conditions</Label>
                {backtestParams.params.conditions.map((condition, index) => 
                  renderConditionInputs(condition, index, false)
                )}
                <Button type="button" variant="outline" className="w-full" onClick={() => addCondition(false)}>
                  <PlusCircle className="mr-2 h-4 w-4" /> Add Condition
                </Button>
              </div>
              <div className="space-y-2">
                <Label>Exit Conditions</Label>
                {backtestParams.params.exits.map((exit, index) => 
                  renderConditionInputs(exit, index, true)
                )}
                <Button type="button" variant="outline" className="w-full" onClick={() => addCondition(true)}>
                  <PlusCircle className="mr-2 h-4 w-4" /> Add Exit
                </Button>
              </div>
              <Button className="w-full" onClick={handleBacktest}>Run Backtest</Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}