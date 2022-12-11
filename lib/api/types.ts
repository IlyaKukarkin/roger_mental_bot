import { ObjectId } from "mongodb";

export type User = {
    form_id: ObjectId;
    telegram_username: string;
    is_volunteer: boolean;
    current_user_time: number;
    result: boolean;
    _id: ObjectId;
    is_admin: boolean;
    is_active: boolean;
    created_at: string;
    time_to_send_messages: number;
    current_time: number;
    user_time: number;
    name: string;
    timezone: string;
    is_banned_from_volunteering: boolean;
    telegram_id: string;
};

export type TgMessage = {
    message_id: number
}