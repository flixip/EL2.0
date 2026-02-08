I will fix the issue where the map and time axis do not correctly reflect the year range and start year from the data.

**Modifications:**

1.  **`src/tools/tableManager.ts`**:
    *   Add a `startYear` reactive property (defaulting to 2000).
    *   Update `aggregateData` method to automatically detect the start year from the CSV headers (by parsing the first value field).
    *   Update `startYear` based on the minimum detected year from all imported CSVs.

2.  **`src/tools/mapManager.ts`**:
    *   Update the constructor to watch `tableManager.startYear` and synchronize it to `timeConfig.startYear`.
    *   Ensure the watcher for `yearRange` uses `{ immediate: true }` to catch the initial state.
    *   Ensure the watcher for `startYear` also uses `{ immediate: true }`.

This ensures that when data is imported, both the range (number of years) and the starting year are correctly propagated to the `MapManager` and `TimeAxis` component.