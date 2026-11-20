create table if not exists books (
    id varchar(36) primary key,
    user_id varchar(50) not null,
    title varchar(100) not null,
    cover_gradient text,
    prologue text,
    epilogue text,
    life_theme varchar(100),
    generation_error text,
    created_at timestamp not null,
    updated_at timestamp not null
);

create index if not exists idx_books_user_created
    on books(user_id, created_at desc);

create table if not exists book_pages (
    id varchar(36) primary key,
    book_id varchar(36) not null references books(id) on delete cascade,
    page_number integer not null,
    chapter varchar(150) not null,
    content text not null,
    episode_id varchar(100)
);

create unique index if not exists uq_book_pages_book_page_number
    on book_pages(book_id, page_number);

create index if not exists idx_book_pages_book_id
    on book_pages(book_id);
