package com.realmone.alpha5_java.repository;

import com.realmone.alpha5_java.entity.XmlFile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface XmlFileRepository extends JpaRepository<XmlFile, String>{
    XmlFile findByIdentifier(String identifier);
    void deleteByIdentifier(String identifier);
}
