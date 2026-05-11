create table if not exists user_profile (
    user_id bigint not null,
    user_title varchar(10) not null,
    age_group varchar(30) not null,
    speech_level varchar(20) not null,
    has_children boolean not null,
    happiest_moment varchar(200),
    onboarding_completed boolean not null,
    completed_at timestamp,
    core_values varchar(200),
    extra_value varchar(7),
    guide_completed boolean not null default false,
    primary key (user_id)
);

create table if not exists interview_session (
    session_id varchar(36) not null,
    user_id bigint not null,
    started_at timestamp not null,
    ended_at timestamp,
    end_reason varchar(30),
    status varchar(10) not null,
    primary key (session_id)
);

create table if not exists turn_log (
    turn_id varchar(36) not null,
    session_id varchar(36) not null,
    user_id bigint not null,
    request_id varchar(36) not null,
    ts timestamp not null,
    input_mode varchar(20) not null,
    user_text text not null,
    reply text not null,
    question text not null,
    raw_model_output text,
    prompt_version varchar(50) not null,
    model varchar(50) not null,
    latency_ms bigint not null,
    primary key (turn_id)
);

create unique index if not exists uq_turn_log_session_request
    on turn_log (session_id, request_id);

create index if not exists idx_turn_log_session_ts
    on turn_log (session_id, ts);

create table if not exists essay (
    essay_id varchar(36) not null,
    user_id bigint not null,
    session_id varchar(36) not null,
    title varchar(80) not null,
    content text not null,
    summary text,
    representative_year integer,
    category varchar(40),
    thumbnail_url varchar(500),
    image_prompt text,
    pdf_url varchar(500),
    emotion_label varchar(40),
    emotion_score integer,
    created_at timestamp not null,
    updated_at timestamp not null,
    primary key (essay_id)
);

create unique index if not exists uq_essay_session
    on essay (session_id);

create index if not exists idx_essay_user_created
    on essay (user_id, created_at desc);

create index if not exists idx_essay_user_year
    on essay (user_id, representative_year);

create table if not exists essay_comment (
    comment_id varchar(36) not null,
    essay_id varchar(36) not null,
    user_id bigint not null,
    author_name varchar(30) not null,
    content text not null,
    created_at timestamp not null,
    primary key (comment_id)
);

create index if not exists idx_essay_comment_essay_created
    on essay_comment (essay_id, created_at);

create index if not exists idx_essay_comment_user_created
    on essay_comment (user_id, created_at desc);

create table if not exists share_link (
    share_id varchar(36) not null,
    essay_id varchar(36) not null,
    user_id bigint not null,
    token varchar(64) not null unique,
    created_at timestamp not null,
    expires_at timestamp,
    primary key (share_id)
);
