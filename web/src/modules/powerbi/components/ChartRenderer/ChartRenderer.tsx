import React from "react";
import {
  LineChart, Line,
  BarChart, Bar,
  AreaChart, Area,
  PieChart, Pie, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, Tooltip, Legend, CartesianGrid,
  ResponsiveContainer
} from "recharts";

interface ChartRendererProps {
  type: string;
  data: any[];
  xField?: string;
  yField?: string;
  series?: string[];
  colors?: string[];
  config?: Record<string, any>;
}

const defaultColors = [
  "#8884d8", "#82ca9d", "#ffc658",
  "#ff8042", "#00C49F", "#0088FE",
];

export const ChartRenderer: React.FC<ChartRendererProps> = ({
  type,
  data,
  xField,
  yField,
  series = [],
  colors = defaultColors,
  config = {},
}) => {

  // ---------------------------
  // 🔹 Render: KPI Card
  // ---------------------------
  if (type === "kpi") {
    const value = data?.[0]?.[yField ?? "value"];
    return (
      <div className="w-full h-full flex flex-col items-center justify-center p-6 bg-white shadow rounded-xl">
        <div className="text-4xl font-bold">{value}</div>
        <div className="text-gray-600">{config.label ?? "KPI"}</div>
      </div>
    );
  }

  // ---------------------------
  // 🔹 Render: Table
  // ---------------------------
  if (type === "table") {
    if (!data || !Array.isArray(data)) return null;
    const cols = Object.keys(data[0] || {});
    return (
      <div className="overflow-auto w-full h-full bg-white shadow rounded-xl p-4">
        <table className="min-w-full border">
          <thead>
            <tr>
              {cols.map(c => (
                <th key={c} className="border px-2 py-1 text-left bg-gray-100 font-medium">
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx} className="border-t">
                {cols.map(c => (
                  <td key={c} className="border px-2 py-1">
                    {row[c]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  // ---------------------------
  // 🔹 Graphs that use Recharts
  // ---------------------------
  return (
    <ResponsiveContainer width="100%" height="100%">
      <>
      {type === "line" && (
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} />
          <YAxis />
          <Tooltip />
          <Legend />
          {series.map((s, i) => (
            <Line
              key={s}
              type="monotone"
              dataKey={s}
              stroke={colors[i % colors.length]}
              dot={false}
            />
          ))}
        </LineChart>
      )}

      {type === "bar" && (
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} />
          <YAxis />
          <Tooltip />
          <Legend />
          {series.map((s, i) => (
            <Bar
              key={s}
              dataKey={s}
              fill={colors[i % colors.length]}
            />
          ))}
        </BarChart>
      )}

      {type === "area" && (
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} />
          <YAxis />
          <Tooltip />
          <Legend />
          {series.map((s, i) => (
            <Area
              key={s}
              type="monotone"
              dataKey={s}
              fill={colors[i % colors.length]}
              stroke={colors[i % colors.length]}
            />
          ))}
        </AreaChart>
      )}

      {type === "pie" && (
        <PieChart>
          <Pie
            data={data}
            dataKey={yField ?? "value"}
            nameKey={xField ?? "name"}
            outerRadius={90}
            label
          >
            {data.map((_, i) => (
              <Cell key={i} fill={colors[i % colors.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      )}

      {type === "radar" && (
        <RadarChart data={data}>
          <PolarGrid />
          <PolarAngleAxis dataKey={xField} />
          <PolarRadiusAxis />
          {series.map((s, i) => (
            <Radar
              key={s}
              name={s}
              dataKey={s}
              stroke={colors[i % colors.length]}
              fill={colors[i % colors.length]}
              fillOpacity={0.6}
            />
          ))}
          <Legend />
        </RadarChart>
      )}
      </>
    </ResponsiveContainer>
  );
};

export default ChartRenderer;
