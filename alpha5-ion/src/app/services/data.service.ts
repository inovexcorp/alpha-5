import { Injectable } from '@angular/core';

export interface Message {
  fromName: string;
  subject: string;
  date: string;
  id: number;
  read: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class DataService {
  // add more options to the list here
  public messages: Message[] = [
    {
      fromName: 'Upload',
      subject: 'Upload a new XML File',
      date: '',
      id: 0,
      read: true
    },
    {
      fromName: 'View',
      subject: 'View a list of previously uploaded files',
      date: '',
      id: 1,
      read: true
    }
  ];

  constructor() { }

  public getMessages(): Message[] {
    return this.messages;
  }

  public getMessageById(id: number): Message {
    return this.messages[id];
  }
}
