'use client';

import { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { formatCurrency } from '@/lib/utils';
import { Search, ArrowUpDown, ArrowUp, ArrowDown, TrendingUp, TrendingDown } from 'lucide-react';
import type { ProviderName } from '@/lib/types';

export interface CostBreakdownItem {
  id: string;
  name: string;
  provider: ProviderName;
  type: string;
  cost: number;
  usage: number;
  usageUnit: string;
  trend?: 'up' | 'down' | 'stable';
  trendPercentage?: number;
  status: 'active' | 'inactive' | 'pending';
  lastUpdated: string;
}

interface CostBreakdownTableProps {
  items: CostBreakdownItem[];
  showTrend?: boolean;
  onItemClick?: (item: CostBreakdownItem) => void;
}

type SortField = 'name' | 'provider' | 'cost' | 'usage' | 'lastUpdated';
type SortOrder = 'asc' | 'desc';

export function CostBreakdownTable({ items, showTrend = true, onItemClick }: CostBreakdownTableProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState<SortField>('cost');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [filterProvider, setFilterProvider] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const providers = useMemo(() => {
    const uniqueProviders = new Set(items.map(item => item.provider));
    return Array.from(uniqueProviders);
  }, [items]);

  const filteredAndSortedItems = useMemo(() => {
    let filtered = items;

    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.provider.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.type.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (filterProvider !== 'all') {
      filtered = filtered.filter(item => item.provider === filterProvider);
    }

    if (filterStatus !== 'all') {
      filtered = filtered.filter(item => item.status === filterStatus);
    }

    return filtered.sort((a, b) => {
      let aValue: any = a[sortField];
      let bValue: any = b[sortField];

      if (sortField === 'lastUpdated') {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }, [items, searchQuery, sortField, sortOrder, filterProvider, filterStatus]);

  const totals = useMemo(() => {
    return filteredAndSortedItems.reduce(
      (acc, item) => ({
        cost: acc.cost + item.cost,
        items: acc.items + 1,
      }),
      { cost: 0, items: 0 }
    );
  }, [filteredAndSortedItems]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return <ArrowUpDown className="ml-2 h-4 w-4" />;
    return sortOrder === 'asc' ? 
      <ArrowUp className="ml-2 h-4 w-4" /> : 
      <ArrowDown className="ml-2 h-4 w-4" />;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/10 text-green-700 border-green-500/20';
      case 'inactive':
        return 'bg-gray-500/10 text-gray-700 border-gray-500/20';
      case 'pending':
        return 'bg-yellow-500/10 text-yellow-700 border-yellow-500/20';
      default:
        return '';
    }
  };

  const getTrendIcon = (trend?: 'up' | 'down' | 'stable') => {
    if (!trend || trend === 'stable') return null;
    return trend === 'up' ? 
      <TrendingUp className="h-3 w-3 text-red-500" /> : 
      <TrendingDown className="h-3 w-3 text-green-500" />;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Cost Breakdown</CardTitle>
            <CardDescription>
              Detailed view of deployment costs and usage
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Total Cost</p>
              <p className="text-2xl font-bold">{formatCurrency(totals.cost)}</p>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search deployments..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8"
            />
          </div>
          <div className="flex gap-2">
            <Select value={filterProvider} onValueChange={setFilterProvider}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Provider" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Providers</SelectItem>
                {providers.map(provider => (
                  <SelectItem key={provider} value={provider}>
                    {provider.charAt(0).toUpperCase() + provider.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort('name')}
                    className="h-8 px-2"
                  >
                    Deployment
                    {getSortIcon('name')}
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort('provider')}
                    className="h-8 px-2"
                  >
                    Provider
                    {getSortIcon('provider')}
                  </Button>
                </TableHead>
                <TableHead>Type</TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort('usage')}
                    className="h-8 px-2"
                  >
                    Usage
                    {getSortIcon('usage')}
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort('cost')}
                    className="h-8 px-2"
                  >
                    Cost
                    {getSortIcon('cost')}
                  </Button>
                </TableHead>
                {showTrend && <TableHead>Trend</TableHead>}
                <TableHead>Status</TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort('lastUpdated')}
                    className="h-8 px-2"
                  >
                    Last Updated
                    {getSortIcon('lastUpdated')}
                  </Button>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAndSortedItems.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={showTrend ? 8 : 7} className="text-center py-8">
                    <p className="text-muted-foreground">No deployments found</p>
                  </TableCell>
                </TableRow>
              ) : (
                filteredAndSortedItems.map((item) => (
                  <TableRow
                    key={item.id}
                    className="cursor-pointer"
                    onClick={() => onItemClick?.(item)}
                  >
                    <TableCell className="font-medium">{item.name}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {item.provider}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{item.type}</TableCell>
                    <TableCell>
                      {item.usage.toLocaleString()} {item.usageUnit}
                    </TableCell>
                    <TableCell className="font-medium">
                      {item.cost === 0 ? (
                        <Badge variant="outline" className="bg-green-500/10 text-green-700 border-green-500/20">
                          Free
                        </Badge>
                      ) : (
                        formatCurrency(item.cost)
                      )}
                    </TableCell>
                    {showTrend && (
                      <TableCell>
                        {item.trend && item.trend !== 'stable' && item.trendPercentage ? (
                          <div className="flex items-center gap-1">
                            {getTrendIcon(item.trend)}
                            <span className={`text-xs ${item.trend === 'up' ? 'text-red-500' : 'text-green-500'}`}>
                              {item.trendPercentage.toFixed(1)}%
                            </span>
                          </div>
                        ) : (
                          <span className="text-xs text-muted-foreground">-</span>
                        )}
                      </TableCell>
                    )}
                    <TableCell>
                      <Badge variant="secondary" className={getStatusColor(item.status)}>
                        {item.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {new Date(item.lastUpdated).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        <div className="flex items-center justify-between text-sm text-muted-foreground border-t pt-4">
          <div>
            Showing {filteredAndSortedItems.length} of {items.length} deployments
          </div>
          <div className="flex items-center gap-4">
            <div>
              Average: {formatCurrency(totals.items > 0 ? totals.cost / totals.items : 0)}
            </div>
            <div className="font-medium text-foreground">
              Total: {formatCurrency(totals.cost)}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
