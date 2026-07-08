"""Manifest for the band-resolution submission docs (the world half of the band_report seam).

ONE entry per recorded task = one row of the master table + one per-task record. Scores are inlined
(from the existing eval rollouts) so `tools/band_report_impute.py` regenerates every record + row with
NO API calls, NO re-execution, NO new eval runs. The generator computes band / spread / sigma_abs /
#band_supports / #observed / verdict from these numbers + the committed npz (static offline resolution),
and the SDK `band_report` renders the two files.

Per entry:
  cfg          module path holding the task CONFIG dict (npz_name, target_cols, categorical_cols, rate, n_test).
  npz          committed data file (for the static class/dispersion structure behind sigma).
  eval         primary eval id (for the eval8 record-dir + the run link).
  scores       every run's recovery score (from the rollouts). The band is built from these.
  task_url     hosted task page.
  evals        [(label, url), ...] hosted eval pages.
  submit       world-authored col-7 text ("**YES**" / "NO (floored)" ...). If omitted, auto from #band_supports.
  verdict_line world-authored one-liner. If omitted, auto from #band_supports.
  slot         2x2^3 grid coordinate "type/#cols/coamp/dataset" (for the grid-map section; not used by the SDK).
  supersedes   optional note when a task replaces an earlier floored attempt.
  narrative    optional {title -> markdown} extra record sections (strategy analysis for the tasks we dug into).
"""
_T = "https://horizon.bespokelabs.ai/tasks/"
_E = "https://horizon.bespokelabs.ai/evaluations/"

MANIFEST = {
    # ── Numeric · California / Covertype ───────────────────────────────────────────
    "california-impute-direct": dict(
        cfg="tasks_def.configs.california_direct", npz="worlds/imputation/data/california.npz",
        eval="41ae826f-3fec-4b9a-938e-bbcbd0e225df", slot="num/single/no/california",
        scores=[0.3645, 0.4376, 0.4499, 0.4964, 0.5227],
        task_url=_T+"76263f44-25bb-48a4-82f1-6383a214e8f8", evals=[("eval", _E+"41ae826f-3fec-4b9a-938e-bbcbd0e225df")]),
    "covertype-impute-direct-single": dict(
        cfg="tasks_def.configs.covertype_direct_single", npz="worlds/imputation/data/covertype.npz",
        eval="6ce009ad-9656-4c22-8562-b0447e705265", slot="num/single/no/covertype",
        scores=[0.6201, 0.6228, 0.7014, 0.7025, 0.7053], submit="**YES** (clustered)",
        verdict_line="WORKS (clustered): band 0.62-0.71, a 2-vs-3 split; real skill gradient, transductive train+test pooling separates the clusters",
        task_url=_T+"6ed892d5-8d1b-49f2-b70e-df65a6957813", evals=[("eval", _E+"6ce009ad-9656-4c22-8562-b0447e705265")]),
    "california-impute-coamp-single": dict(
        cfg="tasks_def.configs.california_coamp_single", npz="worlds/imputation/data/california.npz",
        eval="0253d895-67be-40b9-a006-15d66a821a7f", slot="num/single/yes/california",
        scores=[0.1507, 0.1521, 0.1923, 0.2106, 0.2619],
        task_url=_T+"f771caff-3d94-42f6-9804-7751bb1e06af", evals=[("eval", _E+"0253d895-67be-40b9-a006-15d66a821a7f")]),
    "covertype-impute-coamp-single": dict(
        cfg="tasks_def.configs.covertype_coamp_single", npz="worlds/imputation/data/covertype.npz",
        eval="63093dca-ac27-48ad-891b-b0485a5c4d63", slot="num/single/yes/covertype",
        scores=[0.5330, 0.5928, 0.6094, 0.6096, 0.6104], submit="NO (clustered)",
        verdict_line="only 3 tiers realized (#obs) of the ~12 the test could resolve: a lone low outlier "
                     "under a converged 0.59-0.61 pack. Rescue re-runs (more test data, harder amputation) "
                     "both re-converged -> intrinsically sample-dependent, eliminated",
        task_url=_T+"d6237f92-5541-495d-a90e-25316f0247b1", evals=[("eval", _E+"63093dca-ac27-48ad-891b-b0485a5c4d63")]),
    "california-impute-direct-multi": dict(
        cfg="tasks_def.configs.california_direct_multi", npz="worlds/imputation/data/california.npz",
        eval="cdb91691-0e32-49fa-a58f-42218dc0f062", slot="num/multi/no/california",
        scores=[0.4033, 0.4608, 0.5684, 0.5745, 0.6005], submit="**YES**",
        verdict_line="WORKS (widest numeric band): 0.40-0.60, evenly spread; real skill gradient, transductive pooling of the per-column fit",
        task_url=_T+"596e923b-bb5d-4dd8-af48-19a2227c0ee0", evals=[("eval", _E+"cdb91691-0e32-49fa-a58f-42218dc0f062")]),
    "covertype-impute-direct": dict(
        cfg="tasks_def.configs.covertype_direct", npz="worlds/imputation/data/covertype.npz",
        eval="c56b6c86-36e5-45da-9f9b-8d40ae038f2b", slot="num/multi/no/covertype",
        scores=[0.2707, 0.2985, 0.3009, 0.3768, 0.3846],
        task_url=_T+"ff227290-a39d-4cf8-a162-4d79b580743f", evals=[("eval", _E+"c56b6c86-36e5-45da-9f9b-8d40ae038f2b")]),
    "california-impute-coamp-multi": dict(
        cfg="tasks_def.configs.california_coamp_multi", npz="worlds/imputation/data/california.npz",
        eval="ba56e09b-b0fb-4c2e-a7ae-49bdcbef8fdc", slot="num/multi/yes/california",
        scores=[0.2702, 0.2976, 0.3287, 0.3456, 0.3945],
        task_url=_T+"ef7addc9-3664-4b21-814d-75d9ae0a8080", evals=[("eval", _E+"ba56e09b-b0fb-4c2e-a7ae-49bdcbef8fdc")]),
    "covertype-impute-coamp-multi": dict(
        cfg="tasks_def.configs.covertype_coamp_multi", npz="worlds/imputation/data/covertype.npz",
        eval="5114329d-9b82-4d24-8759-5cf8031a7f44", slot="num/multi/yes/covertype",
        scores=[0.2877, 0.2882, 0.2906, 0.3002, 0.3290], submit="NO (clustered)",
        verdict_line="tight pack ~0.29 (width 0.04) with one high outlier; rescue re-runs stayed converged "
                     "-> covertype's redundant residual gives intrinsically low separation, eliminated",
        task_url=_T+"9e443879-143e-43f7-a6cb-6c57bdb03239", evals=[("eval", _E+"5114329d-9b82-4d24-8759-5cf8031a7f44")]),

    # ── Categorical · Adult / Bank ─────────────────────────────────────────────────
    "adult-impute-cat-single": dict(
        cfg="tasks_def.configs.adult_cat_single", npz="worlds/imputation/data/adult.npz",
        eval="2be818d8-dd93-4f9b-9143-87112ac09d76", slot="cat/single/no/adult",
        scores=[0.2281, 0.2415, 0.2422, 0.2455, 0.2462], submit="NO (converged)",
        verdict_line="occupation single converges: one classifier recipe -> shared MI ceiling ~0.24",
        task_url=_T+"afba95ba-144c-47bb-9f1b-6707c4eb67fe", evals=[("eval", _E+"2be818d8-dd93-4f9b-9143-87112ac09d76")]),
    "bank-impute-cat-single": dict(
        cfg="tasks_def.configs.bank_cat_single", npz="worlds/imputation/data/bank.npz",
        eval="ec944173-61c8-4030-ab90-96a2d938d93b", slot="cat/single/no/bank",
        scores=[0.2318, 0.2331, 0.2341, 0.2344, 0.2692], submit="NO (converged)",
        verdict_line="job single converges on a 2nd dataset (four runs bunched ~0.233), confirms single-cat convergence",
        task_url=_T+"970837ef-cf77-4717-b134-e5f8b5dd5ffc", evals=[("eval", _E+"ec944173-61c8-4030-ab90-96a2d938d93b")]),
    "adult-impute-cat-coamp-single-occ": dict(
        cfg="tasks_def.configs.adult_cat_coamp_single_occ", npz="worlds/imputation/data/adult.npz",
        eval="56635973-4eea-4d80-9bde-f765ae6f7e9e", slot="cat/single/yes/adult",
        scores=[0.091, 0.1386, 0.1592, 0.1679, 0.1682],
        supersedes="salvages the low-cardinality relationship attempt (adult-impute-cat-coamp-single), which floored",
        task_url=_T+"4d90aba0-2d22-4973-b3d4-204d9f813f24", evals=[("eval", _E+"56635973-4eea-4d80-9bde-f765ae6f7e9e")]),
    "bank-impute-cat-coamp-single-job": dict(
        cfg="tasks_def.configs.bank_cat_coamp_single_job", npz="worlds/imputation/data/bank.npz",
        eval="7f7f6ea9-2ba4-4895-9e75-8349b18aa5d0", slot="cat/single/yes/bank",
        scores=[0.0511, 0.0655, 0.0677, 0.0686, 0.0751], submit="NO (floored)",
        verdict_line="floored: job's single carrier is education; co-amputating it collapses recovery to naive",
        task_url=_T+"6beaf077-62ad-4565-ba11-754036ce1484", evals=[("eval", _E+"7f7f6ea9-2ba4-4895-9e75-8349b18aa5d0")]),
    "adult-impute-cat-multi": dict(
        cfg="tasks_def.configs.adult_cat_multi", npz="worlds/imputation/data/adult.npz",
        eval="b7da47bf-8993-46b4-a1fc-b692b070602e", slot="cat/multi/no/adult",
        scores=[0.3646, 0.3767, 0.3906, 0.4453, 0.4486],
        task_url=_T+"fe13c0a7-39dc-4bbe-95b2-eae213467db3", evals=[("eval", _E+"b7da47bf-8993-46b4-a1fc-b692b070602e")]),
    "bank-impute-cat-multi": dict(
        cfg="tasks_def.configs.bank_cat_multi", npz="worlds/imputation/data/bank.npz",
        eval="175c88fc-d0ca-41e6-ad7f-30bdcdcfd22a", slot="cat/multi/no/bank",
        scores=[0.1419, 0.1899, 0.1903, 0.1975, 0.2269],
        submit="NO (luck)",
        verdict_line="luck near the floor: spread 0.08 is mostly seed-luck (3 mid runs within 0.008 + one high outlier), not a skill gradient; capacity 7.6 overstates realized spread",
        task_url=_T+"f38b591d-24f3-438a-8f52-db48b286c6ea", evals=[("eval", _E+"175c88fc-d0ca-41e6-ad7f-30bdcdcfd22a")]),
    "adult-impute-cat-coamp-multi-mild": dict(
        cfg="tasks_def.configs.adult_cat_coamp_multi_mild", npz="worlds/imputation/data/adult.npz",
        eval="366d5ba6-60b7-4f2d-8f2c-2f132013f325", slot="cat/multi/yes/adult",
        scores=[0.2925, 0.3105, 0.348, 0.3666, 0.3684],
        task_url=_T+"d78859a7-2bf0-4ceb-b54f-79bdd5718d4c", evals=[("eval", _E+"366d5ba6-60b7-4f2d-8f2c-2f132013f325")]),
    "bank-impute-cat-coamp-multi-mild": dict(
        cfg="tasks_def.configs.bank_cat_coamp_multi_mild", npz="worlds/imputation/data/bank.npz",
        eval="f834e331-1ae0-4063-b789-8cbc4193cb4a", slot="cat/multi/yes/bank",
        scores=[0.0645, 0.0663, 0.1024, 0.109, 0.119],
        submit="**YES**",
        verdict_line="viable (moderate confidence): strategy diversity, RandomForest beats HistGradientBoosting on a 2-vs-3 split; spread 0.05 hugs the floor so some coincidence risk (capacity 5.3)",
        task_url=_T+"aaf3e2af-455c-41cd-ad9d-b622be25f6d6", evals=[("eval", _E+"f834e331-1ae0-4063-b789-8cbc4193cb4a")]),

    # ── Superseded / documented dead-ends (real evals, kept for the record) ─────────
    "adult-impute-cat-coamp-single": dict(
        cfg="tasks_def.configs.adult_cat_coamp_single", npz="worlds/imputation/data/adult.npz",
        eval="ef3a3efd-09a0-43fe-a4ba-d970ba310950", slot="cat/single/yes/adult (superseded)",
        scores=[0.0511, 0.0617, 0.0623, 0.0702, 0.0738], submit="NO (floored)",
        verdict_line="low-cardinality relationship (K=6) floored; superseded by adult-impute-cat-coamp-single-occ",
        task_url=_T+"dc36b759-947b-4c4a-96d4-13ba958ee3ff", evals=[("eval", _E+"ef3a3efd-09a0-43fe-a4ba-d970ba310950")]),
    "bank-impute-cat-coamp-single": dict(
        cfg="tasks_def.configs.bank_cat_coamp_single", npz="worlds/imputation/data/bank.npz",
        eval="70d88898-69de-41f1-acc7-14d86f5abf5a", slot="cat/single/yes/bank (superseded)",
        scores=[0.0001, 0.0074, 0.0086, 0.0093, 0.0095], submit="NO (floored)",
        verdict_line="low-cardinality education (K=4) floored to ~0; superseded by bank-impute-cat-coamp-single-job",
        task_url=_T+"0ab1d73b-33a1-4ca5-b9c2-e0313e2453b9", evals=[("eval", _E+"70d88898-69de-41f1-acc7-14d86f5abf5a")]),
    "adult-impute-cat-coamp-multi": dict(
        cfg="tasks_def.configs.adult_cat_coamp_multi", npz="worlds/imputation/data/adult.npz",
        eval="ecee2395-e78b-4b7e-b007-5c0e5bd70099", slot="cat/multi/yes/adult (aggressive variant)",
        scores=[0.2918, 0.2965, 0.3113, 0.3185], submit="NO (over-hardened)",
        verdict_line="co-amputating BOTH educ predictors over-hardened -> converged ~0.30; mild variant is the WORKS one",
        task_url=_T+"e8f5f994-0b95-46bc-a424-43d797c84fe0", evals=[("eval", _E+"ecee2395-e78b-4b7e-b007-5c0e5bd70099")]),
    "diabetes-impute-cat-multi": dict(
        cfg="tasks_def.configs.diabetes_cat_multi", npz="worlds/imputation/data/diabetes.npz",
        eval="", slot="cat/multi/no/diabetes (extra modality)",
        band_note="(3 valid runs + 2 agent crashes on the 90-103-class diag cols; eval id not recorded)",
        scores=[0.26, 0.27, 0.28], submit="NO (converged)",
        verdict_line="clinical modality; 3 valid runs converge ~0.27; marginal",
        task_url=_T+"28bebcc0-f53e-4e2d-8518-5888e7d8c2a8", evals=[]),
}
