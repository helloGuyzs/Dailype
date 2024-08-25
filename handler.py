import json
import psycopg2
import uuid
import re
from datetime import datetime

DB_HOST = "dailype.c7kui26ientd.ap-south-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "dailype1234"

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port="5432",
        )
        print("Connected to RDS successfully!")
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to RDS:", error)
        return None

def create_user(event, context):
    conn = get_db_connection()
    if not conn:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to connect to database"}),
        }

    cursor = conn.cursor()

    try:
        body = json.loads(event.get("body", "{}"))
        full_name = body.get("full_name")
        mob_num = body.get("mob_num")
        pan_num = body.get("pan_num")
        manager_id = body.get("manager_id")

        if not full_name or not mob_num or not pan_num:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"}),
            }

        mob_num = mob_num.replace("+91", "").replace(" ", "").strip()
        if len(mob_num) != 10:
            return {
                
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid mobile number"}),
            }

        pan_num = pan_num.upper()
        if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", pan_num):
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid PAN number"})}

        if manager_id:
            cursor.execute("SELECT 1 FROM managers WHERE manager_id = %s", (manager_id,))
            if cursor.fetchone() is None:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid manager ID"}),
                }

        user_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO users (user_id, full_name, mob_num, pan_num, manager_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, full_name, mob_num, pan_num, manager_id),
        )
        conn.commit()
        return {
            "statusCode": 201,
            "body": json.dumps({"message": "User created successfully"}),
        }
    except Exception as e:
        print("Error in create_user function:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
    finally:
        conn.close()


def get_users(event, context):
    conn = get_db_connection()
    if not conn:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to connect to database"}),
        }

    try:
        cursor = conn.cursor()

        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)

        user_id = body.get("user_id")
        mob_num = body.get("mob_num")
        manager_id = body.get("manager_id")

        query = "SELECT * FROM users"
        params = []

        if user_id:
            query += " WHERE user_id = %s"
            params.append(user_id)
        elif mob_num:
            mob_num = mob_num.replace("+91", "").replace(" ", "").strip()
            query += " WHERE mob_num = %s"
            params.append(mob_num)
        elif manager_id:
            query += " WHERE manager_id = %s"
            params.append(manager_id)

        print("Executing query:", query)  # Debugging output
        print("With params:", params)  # Debugging output

        cursor.execute(query, params)
        rows = cursor.fetchall()
        print("Rows fetched:", rows)  # Debugging output

        users = []
        for row in rows:
            users.append(
                {
                    "user_id": row[0],
                    "full_name": row[1],
                    "mob_num": row[2],
                    "pan_num": row[3],
                    "manager_id": row[4],
                    "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S") if row[5] else None,
                    "updated_at": row[6].strftime("%Y-%m-%d %H:%M:%S") if row[6] else None,
                    "is_active": row[7],
                }
            )

        return {"statusCode": 200, "body": json.dumps({"users": users})}
    except Exception as e:
        print("Error in get_users function:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
    finally:
        if conn:
            conn.close()

def delete_user(event, context):

    conn = get_db_connection()
    if not conn:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to connect to database"}),
        }

    cursor = conn.cursor()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        body = json.loads(event.get("body", "{}"))
        user_id = body.get("user_id")
        mob_num = body.get("mob_num")

        if not user_id and not mob_num:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing user_id or mob_num"}),
            }

        if user_id:
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        elif mob_num:
            mob_num = mob_num.replace("+91", "").replace(" ", "").strip()
            cursor.execute("DELETE FROM users WHERE mob_num = %s", (mob_num,))

        if cursor.rowcount == 0:
            return {"statusCode": 404, "body": json.dumps({"error": "User not found"})}

        conn.commit()
        conn.close()
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "User deleted successfully"}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }


def update_user(event, context):
    conn = get_db_connection()
    if not conn:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to connect to database"}),
        }

    cursor = conn.cursor()
    try:
        body = json.loads(event.get("body", "{}"))
        user_ids = body.get("user_ids")
        update_data = body.get("update_data")

        if not user_ids or not update_data:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing user_ids or update_data"}),
            }

        # Check if user_ids exist in the database
        cursor.execute("SELECT user_id FROM users WHERE user_id IN %s", (tuple(user_ids),))
        existing_user_ids = {row[0] for row in cursor.fetchall()}

        not_found_user_ids = set(user_ids) - existing_user_ids
        if not_found_user_ids:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"User IDs {', '.join(not_found_user_ids)} not found"}),
            }

        # Check if manager_id exists in managers' table
        if "manager_id" in update_data:
            manager_id = update_data["manager_id"]
            cursor.execute("SELECT manager_id FROM managers WHERE manager_id = %s", (manager_id,))
            if not cursor.fetchone():
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Manager ID does not exist"})
                }

        if len(update_data) > 1 and "manager_id" not in update_data:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Bulk updates are only allowed for manager_id"})
            }

        for user_id in user_ids:
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()
            if not row:
                continue

            if "manager_id" in update_data:
                if row[4]:  # If manager_id already exists
                    # Deactivate old entry
                    cursor.execute("UPDATE users SET is_active = FALSE, updated_at = %s WHERE user_id = %s", (datetime.utcnow(), user_id))
                    # Insert new entry with updated manager_id
                    cursor.execute(
                        """
                        INSERT INTO users (user_id, full_name, mob_num, pan_num, manager_id, created_at, updated_at, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id) DO UPDATE
                        SET manager_id = EXCLUDED.manager_id, updated_at = EXCLUDED.updated_at
                        """,
                        (
                            user_id,
                            row[1],
                            row[2],
                            row[3],
                            update_data["manager_id"],
                            row[5],
                            datetime.utcnow(),
                            True,
                        ),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO users (user_id, full_name, mob_num, pan_num, manager_id, created_at, updated_at, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id) DO UPDATE
                        SET manager_id = EXCLUDED.manager_id, updated_at = EXCLUDED.updated_at
                        """,
                        (
                            user_id,
                            row[1],
                            row[2],
                            row[3],
                            update_data["manager_id"],
                            row[5],
                            datetime.utcnow(),
                            True,
                        ),
                    )
            else:
                # Update other fields
                cursor.execute(
                    """
                    INSERT INTO users (user_id, full_name, mob_num, pan_num, manager_id, created_at, updated_at, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE
                    SET full_name = EXCLUDED.full_name,
                        mob_num = EXCLUDED.mob_num,
                        pan_num = EXCLUDED.pan_num,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        user_id,
                        update_data.get("full_name", row[1]),
                        update_data.get("mob_num", row[2]),
                        update_data.get("pan_num", row[3]),
                        row[4],
                        row[5],
                        datetime.utcnow(),
                        True,
                    ),
                )

        conn.commit()
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Users updated successfully"}),
        }
    except Exception as e:
        print("Error in update_user function:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
    finally:
        if conn:
            conn.close()