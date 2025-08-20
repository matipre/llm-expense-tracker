/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> } 
 */
exports.seed = async function(knex) {
  // Deletes ALL existing entries
  await knex('users').del();
  
  // Inserts seed entries
  await knex('users').insert([
    { telegram_id: '123456789' }, // Test user 1
    { telegram_id: '987654321' }  // Test user 2
  ]);
};
