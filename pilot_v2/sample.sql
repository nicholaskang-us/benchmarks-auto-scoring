-- 500 reproducible random PUBLIC benchmark tasks + deterministic crit4/crit5 inputs
WITH sample AS (
  SELECT t.Id AS task_id, t.Slug AS task_slug, t.OwnerUserId, t.CurrentVersionId,
         t.SourceKernelId
  FROM `kaggle-infra-analytics.kaggle_prod.BenchmarkTasks` t
  WHERE t.IsPublic AND t.RemoveTime IS NULL AND t.CurrentVersionId IS NOT NULL
  ORDER BY FARM_FINGERPRINT(CAST(t.Id AS STRING))
  LIMIT 500
),
-- per-model average score across this task's completed runs (any version of the task)
model_scores AS (
  SELECT s.task_id, mv.BenchmarkModelId AS model_id,
         AVG(r.NumericResult) AS model_score
  FROM sample s
  JOIN `kaggle-infra-analytics.kaggle_prod.BenchmarkTaskVersions` tv
    ON tv.BenchmarkTaskId = s.task_id
  JOIN `kaggle-infra-analytics.kaggle_prod.BenchmarkRuns` r
    ON r.BenchmarkTaskVersionId = tv.Id
   AND r.State = 3 AND r.RemoveTime IS NULL AND r.NumericResult IS NOT NULL
  JOIN `kaggle-infra-analytics.kaggle_prod.BenchmarkModelVersions` mv
    ON mv.Id = r.BenchmarkModelVersionId
  GROUP BY s.task_id, mv.BenchmarkModelId
),
runs_agg AS (
  SELECT task_id,
         COUNT(DISTINCT model_id) AS distinct_models,
         MIN(model_score) AS min_score,
         MAX(model_score) AS max_score
  FROM model_scores
  GROUP BY task_id
)
SELECT
  s.task_id,
  tv.Name AS task_name,
  CONCAT('https://www.kaggle.com/benchmarks/tasks/', ou.UserName, '/', s.task_slug) AS task_url,
  CASE WHEN k.Id IS NOT NULL AND ku.UserName IS NOT NULL AND k.CurrentUrlSlug IS NOT NULL
       THEN CONCAT('https://www.kaggle.com/code/', ku.UserName, '/', k.CurrentUrlSlug)
       ELSE '' END AS notebook_url,
  s.SourceKernelId AS source_kernel_id,
  COALESCE(ra.distinct_models, 0) AS distinct_models,
  ra.min_score, ra.max_score,
  -- crit 4: model coverage
  CASE WHEN COALESCE(ra.distinct_models,0) >= 4 THEN 2
       WHEN COALESCE(ra.distinct_models,0) IN (2,3) THEN 1
       ELSE 0 END AS crit4,
  -- crit 5: discrimination (<=1 model -> 0; else pass if gap > eps; eps=0.05 on 0-1 scale, 5 on 0-100)
  CASE WHEN COALESCE(ra.distinct_models,0) <= 1 THEN 0
       WHEN (ra.max_score - ra.min_score) > (CASE WHEN ra.max_score <= 1.0 THEN 0.05 ELSE 5.0 END) THEN 2
       ELSE 0 END AS crit5
FROM sample s
JOIN `kaggle-infra-analytics.kaggle_prod.BenchmarkTaskVersions` tv ON tv.Id = s.CurrentVersionId
LEFT JOIN `kaggle-infra-analytics.kaggle_prod.Users` ou ON ou.Id = s.OwnerUserId
LEFT JOIN `kaggle-infra-analytics.kaggle_prod.Kernels` k ON k.Id = s.SourceKernelId
LEFT JOIN `kaggle-infra-analytics.kaggle_prod.Users` ku ON ku.Id = k.AuthorUserId
LEFT JOIN runs_agg ra ON ra.task_id = s.task_id
ORDER BY s.task_id
