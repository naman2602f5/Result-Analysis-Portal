CREATE DEFINER=`root`@`localhost` PROCEDURE `p_results_ins`(
IN p_class_id INT, IN p_roll_no VARCHAR(45), IN p_s01 VARCHAR(45), IN p_s02 VARCHAR(45), IN p_s03 VARCHAR(45), 
IN p_s04 VARCHAR(45), IN p_s05 VARCHAR(45), IN p_s06 VARCHAR(45), IN p_s07 VARCHAR(45), IN p_s08 VARCHAR(45), 
IN p_s09 VARCHAR(45), IN p_s10 VARCHAR(45)
)
BEGIN
	DECLARE v_student_id INT DEFAULT 0; DECLARE v_registration_id INT DEFAULT 0; DECLARE v_result_id INT DEFAULT 0; 
    DECLARE v_optional_subject_id INT DEFAULT 0; DECLARE v_total_marks INT DEFAULT 0; DECLARE v_mark_obtained INT DEFAULT 0;
    DECLARE v_percentage FLOAT DEFAULT 0.0; DECLARE v_division VARCHAR(45) DEFAULT ""; DECLARE v_status VARCHAR(10) DEFAULT "";
        
  SELECT student_id INTO v_student_id FROM students WHERE roll_number = p_roll_no;
	IF (v_student_id > 0) THEN 
    BEGIN 
	   SELECT registration_id INTO v_registration_id FROM registrations WHERE student_id = v_student_id AND class_id = p_class_id;
       SELECT optional_subject_id INTO v_optional_subject_id FROM registrations WHERE student_id = v_student_id AND class_id = p_class_id;
       IF (v_registration_id > 0) THEN 
       BEGIN
			DELETE FROM result_details WHERE result_id = (SELECT result_id FROM results WHERE registration_id = v_registration_id);
            DELETE FROM results WHERE registration_id = v_registration_id;
            
			INSERT INTO results (registration_id) VALUES (v_registration_id);
			SELECT last_insert_id() INTO v_result_id;
            
            INSERT INTO result_details(result_id, subject_id, total_marks, mark_obtained, status)
				VALUES(v_result_id, 1, 100, CAST(p_s01 AS UNSIGNED), IF(CAST(p_s01 AS UNSIGNED) < 33, "F", "P"));
			INSERT INTO result_details(result_id, subject_id, total_marks, mark_obtained, status)
				VALUES(v_result_id, 2, 100, CAST(p_s02 AS UNSIGNED), IF(CAST(p_s02 AS UNSIGNED) < 33, "F", "P"));
			INSERT INTO result_details(result_id, subject_id, total_marks, mark_obtained, status)
				VALUES(v_result_id, 3, 100, CAST(p_s03 AS UNSIGNED), IF(CAST(p_s03 AS UNSIGNED) < 33, "F", "P"));
			INSERT INTO result_details(result_id, subject_id, total_marks, mark_obtained, status)
				VALUES(v_result_id, 4, 100, CAST(p_s04 AS UNSIGNED), IF(CAST(p_s04 AS UNSIGNED) < 33, "F", "P"));
			INSERT INTO result_details(result_id, subject_id, total_marks, mark_obtained, status)
				VALUES(v_result_id, 5, 100, CAST(p_s05 AS UNSIGNED), IF(CAST(p_s05 AS UNSIGNED) < 33, "F", "P"));
			INSERT INTO result_details(result_id, subject_id, total_marks, mark_obtained, status)
				VALUES(v_result_id, 6, 100, CAST(p_s06 AS UNSIGNED), IF(CAST(p_s06 AS UNSIGNED) < 33, "F", "P"));
			
            IF (v_optional_subject_id = 7) THEN 
				INSERT INTO result_details(result_id, subject_id, total_marks, mark_obtained, status)
				VALUES(v_result_id, 7, 100, IF(IFNULL(p_s07,"") = "", 0, CAST(p_s07 AS UNSIGNED)), "");
			ELSEIF (v_optional_subject_id = 8) THEN 
				INSERT INTO result_details(result_id, subject_id, total_marks, mark_obtained, status)
				VALUES(v_result_id, 8, 100, IF(IFNULL(p_s08,"") = "", 0, CAST(p_s08 AS UNSIGNED)), "");
			ELSEIF (v_optional_subject_id = 9) THEN 
				INSERT INTO result_details(result_id, subject_id, total_marks, mark_obtained, status)
				VALUES(v_result_id, 9, 100, IF(IFNULL(p_s09,"") = "", 0, CAST(p_s09 AS UNSIGNED)), "");
			ELSEIF (v_optional_subject_id = 10) THEN 
				INSERT INTO result_details(result_id, subject_id, total_marks, mark_obtained, status)
				VALUES(v_result_id, 10, 100, IF(IFNULL(p_s10,"") = "", 0, CAST(p_s10 AS UNSIGNED)), "");
			END IF;
            
            SELECT SUM(total_marks) INTO v_total_marks FROM result_details WHERE result_id = v_result_id;
            SELECT SUM(mark_obtained) INTO v_mark_obtained FROM result_details WHERE result_id = v_result_id;
            
            IF (SELECT COUNT(*) FROM result_details WHERE result_id = v_result_id AND subject_id <= 6 AND status = "F") > 0 THEN
				SET v_status = "F";
            END IF;
            
            SET v_percentage = (v_mark_obtained * 100) / v_total_marks;
            SET v_division = CASE WHEN v_status = "F" THEN "F"
							WHEN v_percentage < 33 THEN "F"
							WHEN v_percentage < 45 THEN "3rd"
                            WHEN v_percentage < 60 THEN "2nd"
                            WHEN v_percentage < 75 THEN "1st"
                            WHEN v_percentage >= 75 THEN "D"
                            ELSE "" END;
            
            UPDATE results SET total_marks = v_total_marks, mark_obtained = v_mark_obtained, percentage = v_percentage,
				division = v_division
            WHERE result_id = v_result_id;
		END;
        END IF;
	END;
	END IF;  
	
   
   
END