import client from "./authService.js";

export const checkAnalyticsAccess = (signal) => client.get("/admin/analytics/access", { signal });
export const getAnalytics = (params, signal) => client.get("/admin/analytics/summary", { params, signal });
export const exportAnalytics = async (params) => {
  const { data } = await client.get("/admin/analytics/export", { params, responseType: "blob" });
  const url = URL.createObjectURL(data);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "edplan-aggregate-report.csv";
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};
