import apiClient from "./apiClient.js";

const base = "/mesa/conversations";
const url = (session) => `${base}/${session.id}`;
const options = (session, signal) => ({
  signal,
  timeout: 24000,
  headers: session?.guest_token ? { "X-Mesa-Guest": session.guest_token } : {},
});

export const createConversation = async (signal) =>
  (await apiClient.post(base, { retain_history: false }, options(null, signal))).data;
export const recentConversations = async (signal) =>
  (await apiClient.get(base, options(null, signal))).data;
export const openConversation = async (session, signal) =>
  (await apiClient.get(url(session), options(session, signal))).data;
export const deleteConversation = (session) => apiClient.delete(url(session), options(session));
export const updateHistory = async (session, retain_history) =>
  (await apiClient.patch(`${url(session)}/history`, { retain_history }, options(session))).data;
export const updateContext = async (session, changes) =>
  (await apiClient.patch(`${url(session)}/context`, changes, options(session))).data;
export const sendMesaTurn = async (session, input, signal) =>
  (await apiClient.post(`${url(session)}/turns`, input, options(session, signal))).data;
export const confirmMesaAction = async (session, id) =>
  (await apiClient.post(`${url(session)}/actions/${id}`, null, options(session))).data;
export const listScenarios = async (session) =>
  (await apiClient.get(`${url(session)}/scenarios`, options(session))).data;
