import { connection } from "../../Database Module/Database Connection/databaseConnect.js";
// determineOnboardingStatus
export function isOnboardingCompleted(user) {
    if (user.onboarding_completed) {
        return true;
    }
    return false;
}

// markOnboardingCompleted
export async function markOnboardingCompleted(userId) {
    try {
        await connection.query(
            `UPDATE users SET onboarding_completed = true WHERE id = ?`,
            [userId]
        );
        return true;
    } catch (err) {
        console.error("Error marking onboarding as completed:", err);
        throw err;
    }
}

