/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.up = async function(knex) {
  console.log('🚀 Attempting to enable pgmq extension...');
  
  // Create queues for telegram message flow using pgmq schema
  await knex.raw(`SELECT pgmq.create('telegram_received_messages')`);
  await knex.raw(`SELECT pgmq.create('telegram_bot_responses')`);
  
  console.log('✅ pgmq extension and queues created successfully');
  console.log('📋 Created queues: telegram_received_messages, telegram_bot_responses');
};

/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.down = async function(knex) {
  console.log('🧹 Dropping pgmq queues...');
  
  // Drop the queues using pgmq schema
  await knex.raw(`SELECT pgmq.drop('telegram_received_messages')`);
  await knex.raw(`SELECT pgmq.drop('telegram_bot_responses')`);
  
  console.log('✅ pgmq queues dropped successfully');
  // Note: We don't drop the extension as other services might be using it
};
