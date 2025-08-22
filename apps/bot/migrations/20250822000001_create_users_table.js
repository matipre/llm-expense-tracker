/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.up = async function(knex) {
  // Create users table
  await knex.schema.createTable('users', (table) => {
    table.increments('id').primary();
    table.text('telegram_id').unique().notNullable();
    table.timestamp('created_at', { useTz: true }).defaultTo(knex.fn.now());
  });

  // Create index on telegram_id
  await knex.schema.table('users', (table) => {
    table.index('telegram_id', 'idx_users_telegram_id');
  });

  // Enable RLS
  await knex.raw('ALTER TABLE users ENABLE ROW LEVEL SECURITY');

  // Create RLS policies
  await knex.raw(`
    CREATE POLICY "Users can view own data" ON users
      FOR SELECT USING (true)
  `);

  await knex.raw(`
    CREATE POLICY "Users can insert own data" ON users
      FOR INSERT WITH CHECK (true)
  `);

  await knex.raw(`
    CREATE POLICY "Users can update own data" ON users
      FOR UPDATE USING (true)
  `);
};

/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.down = async function(knex) {
  // Drop RLS policies
  await knex.raw('DROP POLICY IF EXISTS "Users can update own data" ON users');
  await knex.raw('DROP POLICY IF EXISTS "Users can insert own data" ON users');
  await knex.raw('DROP POLICY IF EXISTS "Users can view own data" ON users');

  // Drop table (which will also drop indexes)
  await knex.schema.dropTableIfExists('users');
};
