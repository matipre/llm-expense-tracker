import { NestFactory } from '@nestjs/core';
import { FastifyAdapter, NestFastifyApplication } from '@nestjs/platform-fastify';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module.js';

async function bootstrap() {
  const app = await NestFactory.create<NestFastifyApplication>(
    AppModule,
    new FastifyAdapter(),
    { logger: ['log', 'error', 'warn', 'debug', 'verbose'] }
  );
  
  // Enable validation pipes
  app.useGlobalPipes(new ValidationPipe({
    transform: true,
    whitelist: true,
  }));
  
  // Enable graceful shutdown
  app.enableShutdownHooks();
  
  const port = process.env.PORT || 3001;
  await app.listen(port, '0.0.0.0');
  console.log(`🚀 Connector Service running on http://localhost:${port}`);
  
  // Graceful shutdown handling
  const gracefulShutdown = (signal: string) => {
    console.log(`🛑 Received ${signal}, starting graceful shutdown...`);
    
    app.close().then(() => {
      console.log('✅ Application terminated gracefully');
      process.exit(0);
    }).catch((error) => {
      console.error('❌ Error during shutdown:', error);
      process.exit(1);
    });
  };
  
  // Handle shutdown signals
  process.on('SIGINT', () => gracefulShutdown('SIGINT'));
  process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
}

bootstrap();
