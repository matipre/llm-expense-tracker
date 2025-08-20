/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.up = function(knex) {
  return knex.schema.createTable('expenses', function(table) {
    table.increments('id').primary();
    table.integer('user_id').unsigned().notNullable();
    table.text('description').notNullable();
    table.decimal('amount', 12, 2).notNullable(); // Using decimal instead of money for better compatibility
    table.text('category').notNullable();
    table.timestamp('added_at').notNullable().defaultTo(knex.fn.now());
    
    table.foreign('user_id').references('id').inTable('users').onDelete('CASCADE');
    
    table.index('user_id');
    table.index('added_at');
  });
};

/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.down = function(knex) {
  return knex.schema.dropTable('expenses');
};
