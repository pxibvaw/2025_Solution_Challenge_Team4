create table if not exists episodes (
    id varchar(50) primary key,
    user_id varchar(50) not null,
    session_id varchar(50) not null,
    title varchar(200) not null,
    narrative text not null,
    quote text,
    time_hint varchar(100),
    period_label varchar(50),
    estimated_year_range varchar(20),
    location varchar(200),
    persons_json text,
    sensory_json text,
    type varchar(30) not null,
    key_scene_type varchar(50),
    theme varchar(100) not null,
    emotion_tone varchar(100) not null,
    emotion_nuance varchar(200),
    autobiography_hint text,
    life_value varchar(100),
    importance_score double precision,
    faithfulness_score double precision,
    coverage_score double precision,
    emotional_authenticity double precision,
    sensory_vividness double precision,
    personal_voice double precision,
    narrative_flow double precision,
    narrative_richness double precision,
    quality_grade varchar(10),
    needs_regeneration boolean,
    source_session_id varchar(50),
    source_turn_start integer,
    source_turn_end integer,
    source_facts_json text,
    is_merged boolean not null default false,
    merged_from varchar(50),
    version integer not null default 1,
    is_selected_for_autobiography boolean not null default false,
    user_edited_title varchar(200),
    user_memo text,
    created_at timestamp not null,
    updated_at timestamp not null
);

create index if not exists idx_episodes_user_id
    on episodes(user_id);

create index if not exists idx_episodes_session_id
    on episodes(session_id);

create table if not exists ai_episode_callback_log (
    session_id varchar(50) primary key,
    user_id varchar(50) not null,
    episodes_created integer not null,
    episodes_merged integer not null,
    weak_episodes integer not null,
    warnings_json text,
    received_at timestamp not null
);
