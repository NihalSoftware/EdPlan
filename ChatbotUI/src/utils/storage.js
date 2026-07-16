const safeWindow = typeof window !== 'undefined' ? window : undefined;

const USER_DATA_KEYS = [
  'AuthToken',
  'UserEmail',
  'UserProfile',
  'University',
  'UniversityUnitId',
  'UniversityState',
  'Programname',
  'Programnameview',
  'universityview',
  'ProgramDegree',
  'SelectedProgram',
  'SelectedDegreeLevel',
  'selectedComponent',
  'EditingPlan',
  'EditingPlanActive',
  'LocalSavedPlans',
  'CompareQueue',
  'LastCollegeDetail',
];

export const load = (key, fallback = null) => {
  if (!safeWindow) return fallback;
  try {
    const value = safeWindow.localStorage.getItem(key);
    return value ? JSON.parse(value) : fallback;
  } catch (error) {
    console.error(`Failed to read ${key} from localStorage`, error);
    return fallback;
  }
};

export const save = (key, value) => {
  if (!safeWindow) return;
  try {
    safeWindow.localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error(`Failed to write ${key} to localStorage`, error);
  }
};

export const remove = (key) => {
  if (!safeWindow) return;
  try {
    safeWindow.localStorage.removeItem(key);
  } catch (error) {
    console.error(`Failed to remove ${key} from localStorage`, error);
  }
};

export const clearUserData = () => {
  if (!safeWindow) return;
  USER_DATA_KEYS.forEach((key) => {
    remove(key);
    try {
      safeWindow.sessionStorage?.removeItem(key);
    } catch (error) {
      console.error(`Failed to remove ${key} from sessionStorage`, error);
    }
  });
};
