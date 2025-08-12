var adminUser = process.env.MONGO_INITDB_ROOT_USERNAME|| "admin";

var adminPassword = process.env.MONGO_INITDB_ROOT_PASSWORD|| "password123";

db = db.getSiblingDB("admin");


db.createUser({
  user: adminUser,
  pwd: adminPassword,
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" },
    { role: "dbAdminAnyDatabase", db: "admin" }
  ]
});

db = db.getSiblingDB("Akiora");

