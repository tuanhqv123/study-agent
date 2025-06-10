import React, { useState, useEffect } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { AreaChart, Area, XAxis, CartesianGrid } from "recharts";
import { supabase } from "@/lib/supabase";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  CartesianGrid as RechartsGrid,
  XAxis as RechartsXAxis,
} from "recharts";
import { ChartLegend, ChartLegendContent } from "@/components/ui/chart";
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from "@/components/ui/table";
import WordCloudContainer from "@/components/WordCloudContainer";

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState([]);
  const [timeRange, setTimeRange] = useState("90d");
  const [fileDaily, setFileDaily] = useState([]);
  const [fileTerms, setFileTerms] = useState([]);
  const [users, setUsers] = useState([]);
  const [agentUsage, setAgentUsage] = useState([]);
  const [responseByAgent, setResponseByAgent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAllData = async () => {
      setLoading(true);
      try {
        // Mock data để test WordCloud
        const mockFileTerms = [
          { word: "react", count: 25 },
          { word: "javascript", count: 20 },
          { word: "component", count: 15 },
          { word: "dashboard", count: 12 },
          { word: "data", count: 10 },
          { word: "chart", count: 8 },
          { word: "user", count: 7 },
          { word: "api", count: 6 },
          { word: "frontend", count: 5 },
          { word: "backend", count: 4 },
        ];

        // Fetch metrics
        const fetchMetrics = async () => {
          try {
            const res = await fetch("/api/messages/metrics/daily");
            const data = await res.json();
            setMetrics(data);
          } catch (error) {
            console.error("Error fetching metrics:", error);
          }
        };

        // Fetch file metrics
        const fetchFileMetrics = async () => {
          try {
            const { data: daily, error: dailyErr } = await supabase
              .from("file_uploads_daily")
              .select("date, total_uploads");
            if (dailyErr) console.error(dailyErr);
            else setFileDaily(daily || []);
          } catch (error) {
            console.error("Error fetching file metrics:", error);
          }
        };

        // Fetch file terms
        const fetchFileTerms = async () => {
          try {
            const { data, error } = await supabase
              .from("file_terms")
              .select("word, count");
            if (error) {
              console.error(error);
              // Use mock data if no real data
              setFileTerms(mockFileTerms);
            } else {
              setFileTerms(data && data.length > 0 ? data : mockFileTerms);
            }
          } catch (error) {
            console.error("Error fetching file terms:", error);
            setFileTerms(mockFileTerms);
          }
        };

        // Fetch users
        const fetchUsers = async () => {
          try {
            const { data, error } = await supabase
              .from("admin_users")
              .select("id, email, user_role, is_connected");
            if (error) console.error(error);
            else setUsers(data || []);
          } catch (error) {
            console.error("Error fetching users:", error);
          }
        };

        // Fetch agent usage
        const fetchAgentUsage = async () => {
          try {
            const { data, error } = await supabase
              .from("agent_usage")
              .select("agent_id, sessions_count");
            if (error) console.error(error);
            else setAgentUsage(data || []);
          } catch (error) {
            console.error("Error fetching agent usage:", error);
          }
        };

        // Fetch response time
        const fetchResponseTime = async () => {
          try {
            const { data, error } = await supabase
              .from("avg_response_time_by_agent")
              .select("agent_id, avg_response_seconds");
            if (error) console.error(error);
            else setResponseByAgent(data || []);
          } catch (error) {
            console.error("Error fetching response time:", error);
          }
        };

        // Execute all fetches
        await Promise.all([
          fetchMetrics(),
          fetchFileMetrics(),
          fetchFileTerms(),
          fetchUsers(),
          fetchAgentUsage(),
          fetchResponseTime(),
        ]);
      } catch (error) {
        console.error("Error in fetchAllData:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, []);

  // Build complete data series for the selected time range, filling missing dates with 0
  const now = new Date();
  let days = 90;
  if (timeRange === "30d") days = 30;
  else if (timeRange === "7d") days = 7;
  const cutoff = new Date(now);
  cutoff.setDate(cutoff.getDate() - days);
  const dateMap = metrics.reduce((acc, { date, total }) => {
    acc[date] = total;
    return acc;
  }, {});
  const chartData = [];
  // Build local date strings (YYYY-MM-DD) to ensure correct timezone handling
  for (let d = new Date(cutoff); d <= now; d.setDate(d.getDate() + 1)) {
    const dateStr = d.toLocaleDateString("en-CA");
    chartData.push({ date: dateStr, total: dateMap[dateStr] || 0 });
  }

  const chartConfig = {
    total: {
      label: "Messages",
      color: "#3b82f6",
    },
  };

  // Config and data for file uploads per day
  const uploadConfig = {
    total_uploads: { label: "Uploads", color: "#3b82f6" },
  };
  // reuse date range for fileDaily
  const uploadData = fileDaily;

  // Colors and config for agent usage pie
  const agentColors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];
  const agentConfig = agentUsage.reduce((acc, u, idx) => {
    acc[u.agent_id] = {
      label: u.agent_id,
      color: agentColors[idx % agentColors.length],
    };
    return acc;
  }, {});

  return (
    <div className="p-6 space-y-6">
      {loading && (
        <div className="flex items-center justify-center p-8">
          <div className="text-lg">Loading dashboard...</div>
        </div>
      )}
      <div className="flex items-center justify-between">
        {/* ...existing code... */}
        <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>
        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger className="w-auto">
            <SelectValue placeholder="Select range" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="90d">Last 90 days</SelectItem>
            <SelectItem value="30d">Last 30 days</SelectItem>
            <SelectItem value="7d">Last 7 days</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Messages Per Day (Last 90 Days)</CardTitle>
          <CardDescription>
            Number of messages sent per day in the system.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-4 pt-0">
          <ChartContainer
            config={chartConfig}
            className="w-full h-[300px] !aspect-auto !justify-start"
          >
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="fillTotal" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid vertical={false} strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                tickFormatter={(value) => {
                  const d = new Date(value);
                  return d.toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                  });
                }}
                minTickGap={20}
              />
              <ChartTooltip
                content={
                  <ChartTooltipContent
                    labelFormatter={(value) =>
                      new Date(value).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                      })
                    }
                  />
                }
              />
              <Area
                type="monotone"
                dataKey="total"
                stroke="#3b82f6"
                fill="url(#fillTotal)"
              />
            </AreaChart>
          </ChartContainer>
        </CardContent>
      </Card>
      {/* File Uploads & Word Cloud */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* File Uploads Per Day */}
        <Card>
          <CardHeader>
            <CardTitle>File Uploads Per Day</CardTitle>
            <CardDescription>Total files uploaded each day</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer
              config={uploadConfig}
              className="w-full h-[300px] !aspect-auto !justify-start"
            >
              <BarChart data={uploadData}>
                <RechartsGrid vertical={false} strokeDasharray="3 3" />
                <RechartsXAxis
                  dataKey="date"
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) =>
                    new Date(v).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    })
                  }
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="total_uploads" fill="#3b82f6" />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>
        {/* Word Cloud of File Content */}
        <Card>
          <CardHeader>
            <CardTitle>Word Cloud</CardTitle>
            <CardDescription>Common terms in uploaded files</CardDescription>
          </CardHeader>
          <CardContent>
            <WordCloudContainer words={fileTerms} />
          </CardContent>
        </Card>
      </div>
      {/* Agent Usage, Response Time, and Users */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Agent Usage Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Agent Usage Distribution</CardTitle>
            <CardDescription>
              Proportion of chat sessions by agent
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center">
            <ChartContainer
              config={agentConfig}
              className="mx-auto aspect-square w-full max-w-[300px]"
            >
              <PieChart>
                <ChartTooltip
                  content={
                    <ChartTooltipContent nameKey="sessions_count" hideLabel />
                  }
                />
                <Pie
                  data={agentUsage}
                  dataKey="sessions_count"
                  nameKey="agent_id"
                  innerRadius={60}
                  outerRadius={100}
                  label
                >
                  {agentUsage.map((entry, idx) => (
                    <Cell
                      key={idx}
                      fill={agentColors[idx % agentColors.length]}
                    />
                  ))}
                </Pie>
                <ChartLegend
                  content={
                    <ChartLegendContent
                      nameKey="agent_id"
                      className="-translate-y-2 flex-wrap gap-2 *:basis-1/4 *:justify-center"
                    />
                  }
                />
              </PieChart>
            </ChartContainer>
          </CardContent>
        </Card>
        {/* Average Response Time by Agent */}
        <Card>
          <CardHeader>
            <CardTitle>Average Response Time by Agent</CardTitle>
            <CardDescription>
              Avg seconds between user message and agent reply
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Agent ID</TableHead>
                  <TableHead>Avg Response (s)</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {responseByAgent.map((r) => (
                  <TableRow key={r.agent_id}>
                    <TableCell>{r.agent_id}</TableCell>
                    <TableCell>{r.avg_response_seconds.toFixed(1)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
        {/* User list table */}
        <Card>
          <CardHeader>
            <CardTitle>Users</CardTitle>
            <CardDescription>
              Current users and university connection status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Connected</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((u) => (
                  <TableRow key={u.id}>
                    <TableCell>{u.email}</TableCell>
                    <TableCell>{u.user_role}</TableCell>
                    <TableCell>{u.is_connected ? "Yes" : "No"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
