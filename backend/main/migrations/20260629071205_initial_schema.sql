-- Add migration script here
create table users (
    id uuid primary key default uuidv7(),
    name varchar(32) not null,
    email varchar(255) not null unique,
    avatar text,
    about text,
    created_at TIMESTAMPTZ not null DEFAULT NOW(),
    updated_at TIMESTAMPTZ not null DEFAULT NOW()
);

CREATE TABLE relationships (
    initiator_id uuid not null REFERENCES users(id),
    receiver_id uuid not null REFERENCES users(id),
    status TEXT NOT NULL CHECK (status IN ('pending', 'friends', 'blocked')),
    created_at TIMESTAMPTZ DEFAULT NOW(), 
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (initiator_id, receiver_id) 
);

CREATE TABLE lol_accounts (
    user_id uuid not null REFERENCES users(id),
    name text not null,
    tagline text not NULL,
    server text not null,
    tier text,
    division int,
    lp int,
    created_at TIMESTAMPTZ not null DEFAULT NOW(),
    updated_at TIMESTAMPTZ not null DEFAULT NOW(),
    PRIMARY KEY (user_id, name, tagline, server) 
);

CREATE TABLE socials (
    user_id uuid not null REFERENCES users(id),
    platform text not null,
    identifier text not NULL,
    created_at TIMESTAMPTZ not null DEFAULT NOW(),
    verified boolean default false,   
    verified_at TIMESTAMPTZ,
    PRIMARY KEY (user_id, platform, identifier) 
);

create table hosts (
    id uuid primary key default uuidv7(),
    owner_id uuid not null REFERENCES users(id),
    name varchar(32) not null,  
    avatar text,
    background text,
    about text,
    created_at TIMESTAMPTZ not null DEFAULT NOW(),
    updated_at TIMESTAMPTZ not null DEFAULT NOW()
);



create table tournaments (
    id uuid primary key default uuidv7(),
    host_id uuid not null REFERENCES hosts(id),
    name varchar(32) not null,
    description text,
    server text not null,
    tournament_type text not null check (tournament_type in ('draft','presigned')),
    status text not null,
    prizepool text,
    start_time TIMESTAMPTZ not null,
    created_at TIMESTAMPTZ not null DEFAULT NOW(),
    updated_at TIMESTAMPTZ not null DEFAULT NOW()
);


create table host_admins (
    user_id uuid not null REFERENCES users(id),
    host_id uuid not null REFERENCES hosts(id),
    created_at TIMESTAMPTZ not null DEFAULT NOW(),
    PRIMARY KEY (user_id, host_id)
);

create table tournament_draft_configs (
    id uuid primary key default uuidv7(),
    tournament_id uuid not null unique REFERENCES tournaments(id),
    draft_start TIMESTAMPTZ not null, 
    draft_algorithm text not null
);

create table teams(
    id uuid PRIMARY key default uuidv7(),
    tournament_id uuid not null REFERENCES tournaments(id),
    name text not null,  
    created_at TIMESTAMPTZ not null DEFAULT NOW()
);

create table draft_pools (
    tournament_draft_config_id uuid not null REFERENCES tournament_draft_configs(id),
    user_id uuid not null REFERENCES users(id),
    primary_role text not null,
    secondary_role text check (secondary_role != primary_role),
    created_at TIMESTAMPTZ not null DEFAULT NOW(),
    is_captain boolean,
    team_id uuid REFERENCES teams(id),
    PRIMARY KEY (tournament_draft_config_id, user_id)
);



create table tournament_presign_configs (
    id uuid primary key default uuidv7(),
    tournament_id uuid not null unique REFERENCES tournaments(id),
    team_size int not null,
    team_max_count int not null
);
create table team_players(
    team_id uuid not null REFERENCES teams(id),
    user_id uuid not null REFERENCES users(id),
    is_captain boolean default false,
    is_drafter boolean default false,
    PRIMARY KEY (team_id, user_id)
);


create table lol_game_series(
    id uuid PRIMARY key default uuidv7(),
    tournament_id uuid not null REFERENCES tournaments(id),
    best_of int not null,
    status text not null,
    team1 uuid not null REFERENCES teams(id),
    team2 uuid not null REFERENCES teams(id),
    draft_type text not null

);
create table lol_game(
    game_series_id uuid not null REFERENCES lol_game_series(id),
    team_blue uuid not null REFERENCES teams(id),
    team_red uuid not null REFERENCES teams(id),
    status text not null,
    winner uuid REFERENCES teams(id),
    finished timestamptz,
    draft jsonb
);

create table brackets (
    tournament_id uuid not null REFERENCES tournaments(id),
    body jsonb,
    bracket_type text not null,
    created_at TIMESTAMPTZ not null DEFAULT NOW(),
    updated_at TIMESTAMPTZ not null DEFAULT NOW(),
    PRIMARY KEY (tournament_id)
);
create table forbidden_champions(
    lol_game_series_id uuid not null REFERENCES lol_game_series(id),
    champion_id int not null,
    PRIMARY KEY (lol_game_series_id, champion_id)
);
