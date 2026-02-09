
// Wrapper for IndexedDB using idb library
const DB_NAME = 'InventoryPredictorDB';
const DB_VERSION = 1;

// Ensure idb is loaded
if (!window.idb) {
  console.error("idb library not loaded!");
}

const dbPromise = idb.openDB(DB_NAME, DB_VERSION, {
  upgrade(db) {
    // Users store
    if (!db.objectStoreNames.contains('users')) {
      db.createObjectStore('users', { keyPath: 'userId' });
    }
    // Products store
    if (!db.objectStoreNames.contains('products')) {
      const productStore = db.createObjectStore('products', { keyPath: 'productId' });
      productStore.createIndex('userId', 'userId', { unique: false });
    }
    // Sales store
    if (!db.objectStoreNames.contains('sales')) {
      const salesStore = db.createObjectStore('sales', { keyPath: 'saleId', autoIncrement: true });
      salesStore.createIndex('productId', 'productId', { unique: false });
      salesStore.createIndex('userId', 'userId', { unique: false });
      salesStore.createIndex('date', 'date', { unique: false });
    }
    // Predictions store
    if (!db.objectStoreNames.contains('predictions')) {
      const predStore = db.createObjectStore('predictions', { keyPath: 'predictionId', autoIncrement: true });
      predStore.createIndex('productId', 'productId', { unique: false });
    }
    console.log("DB Upgraded/Created");
  },
});

window.DB = {
  async get(store, key) {
    return (await dbPromise).get(store, key);
  },
  async getAll(store) {
    return (await dbPromise).getAll(store);
  },
  async put(store, val) {
    return (await dbPromise).put(store, val);
  },
  async add(store, val) {
    return (await dbPromise).add(store, val);
  },
  async delete(store, key) {
    return (await dbPromise).delete(store, key);
  },
  async getFromIndex(store, index, key) {
    return (await dbPromise).getAllFromIndex(store, index, key);
  }
};
