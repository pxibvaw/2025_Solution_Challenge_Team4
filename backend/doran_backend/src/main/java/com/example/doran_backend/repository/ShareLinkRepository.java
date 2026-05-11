package com.example.doran_backend.repository;

import com.example.doran_backend.entity.ShareLink;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ShareLinkRepository extends JpaRepository<ShareLink, String> {

    Optional<ShareLink> findByToken(String token);
}
