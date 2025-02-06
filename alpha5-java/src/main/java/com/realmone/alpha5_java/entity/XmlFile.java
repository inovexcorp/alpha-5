package com.realmone.alpha5_java.entity;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Entity
public class XmlFile {
    @Id
    private String identifier;
    private String file_contents;
    private String file_upload_date;
}
