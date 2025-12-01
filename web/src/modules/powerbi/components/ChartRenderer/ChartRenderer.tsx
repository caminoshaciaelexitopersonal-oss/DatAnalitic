import React from "react";
import {
  LineChart, Line,
  BarChart, Bar,
  AreaChart, Area,
  PieChart, Pie, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ScatterChart, Scatter, ZAxis,
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
  // 🔹 ML Visualizations
  // ---------------------------
  if (type === "feature_importance") {
    return (
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis type="category" dataKey="feature" width={120} />
          <Tooltip />
          <Legend />
          <Bar dataKey="importance" fill={colors[3]} />
        </BarChart>
      </ResponsiveContainer>
    );
  }

  if (type === "confusion_matrix") {
    const matrix = data.matrix || [];
    const labels = data.labels || [];
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <h3 className="text-lg mb-2">Matriz de Confusión</h3>
        <table className="border-collapse">
          <tbody>
            {matrix.map((row: number[], i: number) => (
              <tr key={i}>
                <td className="border p-2 font-bold bg-gray-100">{labels[i]}</td>
                {row.map((cell: number, j: number) => (
                  <td key={j} className={`border p-4 text-center text-lg ${i === j ? 'bg-green-100' : 'bg-red-100'}`}>
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
            <tr>
              <td />
              {labels.map((l: string) => <td key={l} className="p-2 font-bold bg-gray-100 text-center">{l}</td>)}
            </tr>
          </tbody>
        </table>
      </div>
    );
  }

  if (type === "roc_curve") {
    return (
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data.points}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" dataKey="fpr" name="Tasa de Falsos Positivos" />
          <YAxis type="number" dataKey="tpr" name="Tasa de Verdaderos Positivos" />
          <Tooltip />
          <Legend formatter={() => `AUC = ${data.auc?.toFixed(4)}`} />
          <Line type="monotone" dataKey="tpr" stroke={colors[0]} dot={false} name="Curva ROC" />
        </LineChart>
      </ResponsiveContainer>
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

      {(type === "bar" || type === "histogram") && (
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField ?? "name"} />
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

      {type === "scatter" && (
        <ScatterChart>
          <CartesianGrid />
          <XAxis type="number" dataKey={xField} name={xField} />
          <YAxis type="number" dataKey={yField} name={yField} />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Legend />
          <Scatter name="Points" data={data} fill={colors[0]} />
        </ScatterChart>
      )}

      {type === "boxplot" && (
          <BarChart data={data} barGap={-10}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis type="number" domain={['dataMin - 1', 'dataMax + 1']} />
            <Tooltip />
            <Bar dataKey="q1" stackId="a" stroke='none' fill='transparent' tooltipType="none" />
            <Bar dataKey={d => d.q3 - d.q1} stackId="a" fill={colors[0]} name="IQR" />
            {/* Note: This is a simplified boxplot showing the IQR. Whiskers and median line would require a custom shape component. */}
          </BarChart>
      )}

      {type === "heatmap" && (
        <ScatterChart>
            <CartesianGrid />
            <XAxis type="category" dataKey="x" name="X" reversed={config.reversedX ?? false} />
            <YAxis type="category" dataKey="y" name="Y" reversed={config.reversedY ?? false} />
            <ZAxis dataKey="value" range={[100, 1000]} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Legend />
            <Scatter data={data} fill={colors[1]} shape="square" />
        </ScatterChart>
      )}
      </>
    </ResponsiveContainer>
  );
};

export default ChartRenderer;
