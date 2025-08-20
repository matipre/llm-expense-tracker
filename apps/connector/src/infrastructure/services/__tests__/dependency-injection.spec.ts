import { Test, TestingModule } from '@nestjs/testing';
import { SupabaseClient } from '@supabase/supabase-js';
import { SUPABASE_CLIENT } from '../../providers/supabase.provider';

describe('Dependency Injection', () => {
  let supabaseClient: SupabaseClient;

  beforeEach(async () => {
    // Create a mock Supabase client
    const mockSupabaseClient = {
      from: jest.fn(),
      rpc: jest.fn(),
    } as any;

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        {
          provide: SUPABASE_CLIENT,
          useValue: mockSupabaseClient,
        },
      ],
    }).compile();

    supabaseClient = module.get<SupabaseClient>(SUPABASE_CLIENT);
  });

  it('should inject Supabase client successfully', () => {
    expect(supabaseClient).toBeDefined();
    expect(supabaseClient.from).toBeDefined();
    expect(supabaseClient.rpc).toBeDefined();
  });

  it('should allow mocking of client methods', () => {
    const mockResponse = { data: [{ id: 1 }], error: null };
    (supabaseClient.from as jest.Mock).mockReturnValue({
      select: jest.fn().mockReturnValue({
        execute: jest.fn().mockResolvedValue(mockResponse)
      })
    });

    // Test that we can mock the client behavior
    expect(supabaseClient.from).toHaveBeenCalledTimes(0);
    
    const tableQuery = supabaseClient.from('test_table');
    expect(supabaseClient.from).toHaveBeenCalledWith('test_table');
    expect(tableQuery.select).toBeDefined();
  });

  it('demonstrates testability benefits of dependency injection', () => {
    // With DI, we can easily:
    // 1. Mock external dependencies
    // 2. Test different configurations
    // 3. Isolate unit under test
    // 4. Control behavior of dependencies
    
    const mockRpcResponse = { data: { msg_id: 123 }, error: null };
    (supabaseClient.rpc as jest.Mock).mockResolvedValue(mockRpcResponse);

    expect(async () => {
      const result = await supabaseClient.rpc('pgmq_send', { 
        queue_name: 'test', 
        msg: { test: 'data' } 
      });
      expect(result).toEqual(mockRpcResponse);
    }).not.toThrow();
  });
});
