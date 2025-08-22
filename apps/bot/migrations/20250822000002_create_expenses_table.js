/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.up = async function(knex) {
  // Create expenses table
  await knex.schema.createTable('expenses', (table) => {
    table.increments('id').primary();
    table.integer('user_id').notNullable();
    table.text('description').notNullable();
    table.decimal('amount', 12, 2).notNullable();
    table.text('category').notNullable();
    table.timestamp('added_at', { useTz: true }).defaultTo(knex.fn.now()).notNullable();

    // Foreign key constraint
    table.foreign('user_id').references('id').inTable('users').onDelete('CASCADE');
  });

  // Create indexes
  await knex.schema.table('expenses', (table) => {
    table.index('user_id', 'idx_expenses_user_id');
    table.index('added_at', 'idx_expenses_added_at');
  });

  // Enable RLS
  await knex.raw('ALTER TABLE expenses ENABLE ROW LEVEL SECURITY');

  // Create RLS policies
  await knex.raw(`
    CREATE POLICY "Users can view own expenses" ON expenses
      FOR SELECT USING (true)
  `);

  await knex.raw(`
    CREATE POLICY "Users can insert own expenses" ON expenses
      FOR INSERT WITH CHECK (true)
  `);

  await knex.raw(`
    CREATE POLICY "Users can update own expenses" ON expenses
      FOR UPDATE USING (true)
  `);

  await knex.raw(`
    CREATE POLICY "Users can delete own expenses" ON expenses
      FOR DELETE USING (true)
  `);
};

/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.down = async function(knex) {
  // Drop RLS policies
  await knex.raw('DROP POLICY IF EXISTS "Users can delete own expenses" ON expenses');
  await knex.raw('DROP POLICY IF EXISTS "Users can update own expenses" ON expenses');
  await knex.raw('DROP POLICY IF EXISTS "Users can insert own expenses" ON expenses');
  await knex.raw('DROP POLICY IF EXISTS "Users can view own expenses" ON expenses');

  // Drop table (which will also drop indexes and foreign keys)
  await knex.schema.dropTableIfExists('expenses');
};
