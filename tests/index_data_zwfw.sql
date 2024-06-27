/*
 Navicat Premium Data Transfer

 Source Server         : 瀚高-黄金库
 Source Server Type    : PostgreSQL
 Source Server Version : 90426 (90426)
 Source Host           : 192.201.0.3:5432
 Source Catalog        : jgk
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 90426 (90426)
 File Encoding         : 65001

 Date: 26/06/2024 18:41:41
*/


-- ----------------------------
-- Table structure for index_data_zwfw
-- ----------------------------
DROP TABLE IF EXISTS "public"."index_data_zwfw";
CREATE TABLE "public"."index_data_zwfw" (
  "index_code" varchar(255) COLLATE "pg_catalog"."default",
  "index_value" varchar(255) COLLATE "pg_catalog"."default",
  "time_value" varchar(255) COLLATE "pg_catalog"."default",
  "time_unit" varchar(255) COLLATE "pg_catalog"."default",
  "statistics_dim" varchar(255) COLLATE "pg_catalog"."default",
  "area_code" varchar(255) COLLATE "pg_catalog"."default",
  "area_name" varchar(255) COLLATE "pg_catalog"."default",
  "department_id" varchar(255) COLLATE "pg_catalog"."default",
  "department_name" varchar(255) COLLATE "pg_catalog"."default",
  "dimension" varchar(255) COLLATE "pg_catalog"."default",
  "data_timestamp" int8,
  "compute_timestamp" int8,
  "dimension_filter" varchar(255) COLLATE "pg_catalog"."default",
  "index_name" varchar(255) COLLATE "pg_catalog"."default",
  "index_unit" varchar(255) COLLATE "pg_catalog"."default"
)
;
COMMENT ON COLUMN "public"."index_data_zwfw"."index_code" IS '指标编码';
COMMENT ON COLUMN "public"."index_data_zwfw"."index_value" IS '指标值';
COMMENT ON COLUMN "public"."index_data_zwfw"."time_value" IS '时间维度值';
COMMENT ON COLUMN "public"."index_data_zwfw"."time_unit" IS '时间维度';
COMMENT ON COLUMN "public"."index_data_zwfw"."statistics_dim" IS '空间维度';
COMMENT ON COLUMN "public"."index_data_zwfw"."area_code" IS '区划编码';
COMMENT ON COLUMN "public"."index_data_zwfw"."area_name" IS '区划名称';
COMMENT ON COLUMN "public"."index_data_zwfw"."department_id" IS '部门编码';
COMMENT ON COLUMN "public"."index_data_zwfw"."department_name" IS '部门名称';
COMMENT ON COLUMN "public"."index_data_zwfw"."dimension" IS '业务维度';
COMMENT ON COLUMN "public"."index_data_zwfw"."data_timestamp" IS '指标数据时间';
COMMENT ON COLUMN "public"."index_data_zwfw"."compute_timestamp" IS '指标计算时间戳';
COMMENT ON COLUMN "public"."index_data_zwfw"."dimension_filter" IS '是否合计数据(0不是,1是)';
COMMENT ON COLUMN "public"."index_data_zwfw"."index_name" IS '指标名称';
COMMENT ON COLUMN "public"."index_data_zwfw"."index_unit" IS '指标单位';
COMMENT ON TABLE "public"."index_data_zwfw" IS '政务服务相关指标数据（事项、办件、好差评等）';

-- ----------------------------
-- Indexes structure for table index_data_zwfw
-- ----------------------------
CREATE INDEX "idx_area_code" ON "public"."index_data_zwfw" USING btree (
  "area_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_data_timestamp" ON "public"."index_data_zwfw" USING btree (
  "data_timestamp" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_dimension" ON "public"."index_data_zwfw" USING btree (
  "dimension" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_dimension_filter" ON "public"."index_data_zwfw" USING btree (
  "dimension_filter" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_time_unit" ON "public"."index_data_zwfw" USING btree (
  "time_unit" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_time_value" ON "public"."index_data_zwfw" USING btree (
  "time_value" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "index_data_zwfw_area_name_department_name_dimension_index_n_idx" ON "public"."index_data_zwfw" USING btree (
  "area_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "department_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "dimension" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "index_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "zwfw_index1" ON "public"."index_data_zwfw" USING btree (
  "index_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "zwfw_index2" ON "public"."index_data_zwfw" USING btree (
  "area_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "zwfw_index3" ON "public"."index_data_zwfw" USING btree (
  "department_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "zwfw_index4" ON "public"."index_data_zwfw" USING btree (
  "index_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
