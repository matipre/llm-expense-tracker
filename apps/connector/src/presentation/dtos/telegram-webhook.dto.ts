import { IsNumber, IsOptional, IsString, IsBoolean, ValidateNested, IsIn } from 'class-validator';
import { Type } from 'class-transformer';

export class TelegramUserDto {
  @IsNumber()
  id: number;

  @IsBoolean()
  is_bot: boolean;

  @IsString()
  first_name: string;

  @IsOptional()
  @IsString()
  last_name?: string;

  @IsOptional()
  @IsString()
  username?: string;

  @IsOptional()
  @IsString()
  language_code?: string;
}

export class TelegramChatDto {
  @IsNumber()
  id: number;

  @IsOptional()
  @IsString()
  first_name?: string;

  @IsOptional()
  @IsString()
  last_name?: string;

  @IsOptional()
  @IsString()
  username?: string;

  @IsIn(['private', 'group', 'supergroup', 'channel'])
  type: 'private' | 'group' | 'supergroup' | 'channel';
}

export class TelegramMessageDto {
  @IsNumber()
  message_id: number;

  @IsOptional()
  @ValidateNested()
  @Type(() => TelegramUserDto)
  from?: TelegramUserDto;

  @ValidateNested()
  @Type(() => TelegramChatDto)
  chat: TelegramChatDto;

  @IsNumber()
  date: number;

  @IsOptional()
  @IsString()
  text?: string;
}

export class TelegramWebhookDto {
  @IsNumber()
  update_id: number;

  @IsOptional()
  @ValidateNested()
  @Type(() => TelegramMessageDto)
  message?: TelegramMessageDto;
}
