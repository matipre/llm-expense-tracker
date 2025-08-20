/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.up = function(knex) {
  return knex.schema.createTable('message_queue', function(table) {
    table.increments('id').primary();
    table.text('type').notNullable(); // 'telegram_message' or 'bot_response'
    table.jsonb('payload').notNullable();
    table.text('status').notNullable().defaultTo('pending'); // 'pending', 'processing', 'completed', 'failed'
    table.timestamp('timestamp').notNullable().defaultTo(knex.fn.now());
    table.integer('retry_count').defaultTo(0);
    table.timestamp('created_at').defaultTo(knex.fn.now());
    table.timestamp('updated_at').defaultTo(knex.fn.now());
    
    table.index(['type', 'status']);
    table.index('timestamp');
    table.index('status');
  });
};

/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.down = function(knex) {
  return knex.schema.dropTable('message_queue');
};
