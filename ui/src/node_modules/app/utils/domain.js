import * as _ from 'lamb';

export const getNutsId = _.getKey('nuts_id');
export const sortAscByYear = _.sortWith([_.sorter(_.getKey('year'))]);
