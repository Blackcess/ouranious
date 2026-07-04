import { connection } from "../../../../Database Module/Database Connection/databaseConnect.js";
import { DomainError } from "../../../../Domain Errors/domainErrors.js";

// private helper -> pass in the database connection instance 
async function resolveInterestIds(conn, codes) {
    const [rows] = await conn.query(
        `SELECT id, code, label FROM onboarding_interest_types WHERE code IN (?)`,
        [codes]
    );

    const foundCodes = rows.map(r => r.code);

    if (foundCodes.length !== codes.length) {
        const missing = codes.filter(c => !foundCodes.includes(c));
        throw DomainError.invalid(`Invalid interest codes: ${missing.join(", ")}`);
    }

    return rows.map(r => r.id);
}

// ensures that every user has an onboarding profile in the system, creates one if not exists
export async function ensureOnboardingProfile(userId) {
    const [rows] = await connection.query(
        `SELECT id FROM user_onboarding_profiles WHERE user_id = ?`,
        [userId]
    );

    if (rows.length > 0) return;

    await connection.query(
        `INSERT INTO user_onboarding_profiles (user_id) VALUES (?)`,
        [userId]
    );
}


export async function getOnboardingProfile(userId) {
    const [profileRows] = await connection.query(
        `SELECT * FROM user_onboarding_profiles WHERE user_id = ?`,
        [userId]
    );

    if (!profileRows.length) return null;

    const profile = profileRows[0];

    const [interestRows] = await connection.query(
        `SELECT t.code 
         FROM user_onboarding_interests ui
         JOIN onboarding_interest_types t
         ON ui.interest_id = t.id
         WHERE ui.user_id = ?`,
        [userId]
    );

    return {
        ...profile,
        interests: interestRows.map(r => r.code)
    };
}

export async function checkOnboardingStatusFromEmail(email){
    const [profileRows] = await connection.query(`
            SELECT * FROM users WHERE email = ? 
        `,[email]);

    if(!profileRows.length) return null;
    const profile = profileRows[0];
    await ensureOnboardingProfile(profile.id);
    const onboardingStatus = await getOnboardingProfile(profile.id)
    return onboardingStatus;
}

export async function updateIdentity(userId, persona) {
    await connection.query(
        `UPDATE user_onboarding_profiles 
         SET persona = ?, onboarding_stage = GREATEST(onboarding_stage, 1)
         WHERE user_id = ?`,
        [persona, userId]
    );
}

export async function updatePreferences(userId, { acquisition_source, preferred_content_region }) {
    await connection.query(
        `UPDATE user_onboarding_profiles
         SET acquisition_source = COALESCE(?, acquisition_source),
             preferred_content_region = COALESCE(?, preferred_content_region),
             onboarding_stage = GREATEST(onboarding_stage, 3)
         WHERE user_id = ?`,
        [acquisition_source ?? null, preferred_content_region ?? null, userId]
    );
}

export async function updateInterests(userId, interestCodes) {
    const conn = await connection.getConnection();

    try {
        await conn.beginTransaction();

        // 1️⃣ Resolve interest IDs
        const interestIds = await resolveInterestIds(conn, interestCodes);
        console.log("All interests are valid  in router:", interestIds) // log the resolved interest IDs;

        // 2️⃣ Delete old interests
        await conn.query(
            `DELETE FROM user_onboarding_interests WHERE user_id = ?`,
            [userId]
        );

        // 3️⃣ Insert new ones
        const values = interestIds.map(id => [userId, id]);

        await conn.query(
            `INSERT INTO user_onboarding_interests (user_id, interest_id) VALUES ?`,
            [values]
        );

        // 4️⃣ Update onboarding stage
        await conn.query(
            `UPDATE user_onboarding_profiles 
             SET onboarding_stage = GREATEST(onboarding_stage, 2)
             WHERE user_id = ?`,
            [userId]
        );

        await conn.commit();

    } catch (err) {
        await conn.rollback();
        throw err;
    } finally {
        conn.release();
    }
}

export async function completeOnboarding(userId) {
    const conn = await connection.getConnection();

    try {
        await conn.beginTransaction();

        // 1️⃣ check persona
        const [profileRows] = await conn.query(
            `SELECT persona FROM user_onboarding_profiles WHERE user_id = ?`,
            [userId]
        );

        if (!profileRows.length || !profileRows[0].persona) {
            throw DomainError.invalid("Cannot complete onboarding: persona not set");
        }

        // 2️⃣ check interests count
        const [interestRows] = await conn.query(
            `SELECT COUNT(*) as count 
             FROM user_onboarding_interests
             WHERE user_id = ?`,
            [userId]
        );

        if (interestRows[0].count === 0) {
            throw DomainError.invalid("Cannot complete onboarding: no interests selected");
        }

        // 3️⃣ mark complete
        await conn.query(
            `UPDATE user_onboarding_profiles
             SET onboarding_completed = true,
                 onboarding_stage = 999
             WHERE user_id = ?`,
            [userId]
        );

        await conn.commit();

    } catch (err) {
        await conn.rollback();
        throw err;
    } finally {
        conn.release();
    }
}