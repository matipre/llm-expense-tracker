import { Module } from '@nestjs/common';
import { HealthController } from './presentation/controllers/health.controller.js';

@Module({
  imports: [],
  controllers: [HealthController],
  providers: [],
})
export class AppModule {}
